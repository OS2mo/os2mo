# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import APIRouter
from psycopg import Cursor
from psycopg2 import sql
from starlette.status import HTTP_204_NO_CONTENT
from structlog import get_logger

from oio_rest.db import _get_dbname
from oio_rest.db import close_connection
from oio_rest.db import get_new_connection

logger = get_logger()


router = APIRouter()


@contextmanager
def database_snapshot_restore() -> Iterator[Cursor, str, str]:
    # Ideally, we would use settings.db_name directly, but it is overwritten during CI
    # integration tests.
    main_db = _get_dbname()
    snapshot_db = f"{main_db}_snapshot"

    # A database cannot be copied or dropped while it has connections. Create a new
    # database connection to a different one.
    connection = get_new_connection(dbname="postgres")
    with connection.cursor() as cursor:
        # Disallow new connections and terminate existing
        cursor.execute(
            """
            UPDATE pg_database SET datallowconn = FALSE WHERE datname = %s;
            """,
            [main_db],
        )
        cursor.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
            """,
            [main_db],
        )
        # Yield for caller's operation
        yield cursor, sql.Identifier(main_db), sql.Identifier(snapshot_db)
        # Allow connections again
        cursor.execute(
            """
            UPDATE pg_database SET datallowconn = TRUE WHERE datname = %s;
            """,
            [main_db],
        )

    # Whereas the SQLAlchemy async_sessionmaker does pessimistic and transparent error
    # handling, so the callers don't need to, LoRas get_connection() does not.
    # Explicitly close the connection so the next caller gets a fresh, working one.
    close_connection()


@router.post("/database/snapshot", status_code=HTTP_204_NO_CONTENT)
async def snapshot() -> None:
    """
    Snapshot the database.
    """
    logger.warning("Snapshotting database")
    with database_snapshot_restore() as (cursor, main_db, snapshot_db):
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(snapshot_db))
        cursor.execute(
            sql.SQL("CREATE DATABASE {} TEMPLATE {}").format(snapshot_db, main_db)
        )


@router.post("/database/restore", status_code=HTTP_204_NO_CONTENT)
async def restore() -> None:
    """
    Restore database snapshot.
    """
    logger.warning("Restoring database")
    with database_snapshot_restore() as (cursor, main_db, snapshot_db):
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(main_db))
        cursor.execute(
            sql.SQL("CREATE DATABASE {} TEMPLATE {}").format(main_db, snapshot_db)
        )
        # Copying a database does not copy its search path; since we use 'actual_state'
        # instead of the default 'public', we need to re-set it manually.
        cursor.execute(
            sql.SQL("ALTER DATABASE {} SET search_path = actual_state,public").format(
                main_db
            )
        )
