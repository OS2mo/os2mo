# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from contextlib import AbstractAsyncContextManager
from contextlib import asynccontextmanager

from fastapi import APIRouter
from oio_rest.config import Settings as LoraSettings
from oio_rest.config import get_settings as lora_get_settings
from psycopg.errors import UndefinedTable
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT
from structlog import get_logger

from mora import amqp
from mora import db
from mora import depends
from mora.service.org import ConfiguredOrganisation

logger = get_logger()


router = APIRouter()


@router.post("/amqp/emit", status_code=HTTP_204_NO_CONTENT)
async def emit(request: Request, amqp_system: depends.AMQPSystem) -> None:
    """
    Emit queued AMQP events immediately.

    Note that this is only needed for the "new" AMQP subsystem. Events in the old one
    are always sent immediately.
    """
    logger.warning("Emitting AMQP events")
    while True:
        try:
            # The request-wide database session, which is used in almost every other
            # endpoint, cannot be used here, as the database snapshot/rollback
            # forcefully closes all connections, irrevocably destroying the session.
            async with db._get_sessionmaker(request)() as session, session.begin():
                await amqp._emit_events(session, amqp_system)
            return
        except (OperationalError, ProgrammingError) as e:
            if isinstance(e, ProgrammingError) and not isinstance(
                e.orig, UndefinedTable
            ):  # pragma: no cover
                raise
            # The database is unavailable while being snapshot or restored. Retry until
            # we succeed.
            logger.warning("Error emitting AMQP events", error=e)
            await asyncio.sleep(0.5)


@asynccontextmanager
async def superuser_connection(
    lora_settings: LoraSettings,
) -> AbstractAsyncContextManager[AsyncConnection]:
    """Managing databases requires a superuser connection."""
    engine = db.create_engine(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name="postgres",
    )
    # AUTOCOMMIT disables transactions to allow for create/drop database operations
    engine.update_execution_options(isolation_level="AUTOCOMMIT")
    async with engine.connect() as connection:
        yield connection


async def _terminate_database_connections(
    superuser: AsyncConnection, database: str
) -> None:
    await superuser.execute(
        text(
            f"""
            select pg_terminate_backend(pid)
            from pg_stat_activity
            where datname = '{database}' and pid <> pg_backend_pid()
            """
        )
    )


async def _set_database_connectable(
    superuser: AsyncConnection, database: str, allow: bool
) -> None:
    await superuser.execute(
        text(
            f"""
            update pg_database
            set datallowconn = :allow
            where datname = '{database}'
        """
        ),
        dict(allow=allow),
    )


async def drop_database(superuser: AsyncConnection, database: str) -> None:
    await _terminate_database_connections(superuser, database)
    await superuser.execute(text(f"drop database if exists {database}"))


async def copy_database(
    superuser: AsyncConnection, source: str, destination: str
) -> None:
    """Copy database, overwriting (dropping) destination if it already exists."""
    # A database cannot be copied or dropped while it has connections; disallow new
    # connections and terminate existing.
    await _set_database_connectable(superuser, source, False)
    await _set_database_connectable(superuser, destination, False)
    await _terminate_database_connections(superuser, source)
    await _terminate_database_connections(superuser, destination)
    # Copy database
    await drop_database(superuser, destination)
    await superuser.execute(text(f"create database {destination} template {source}"))
    # Copying a database does not copy its configuration parameters. These statements
    # are copied from the initial alembic migration.
    await superuser.execute(
        text(f"ALTER DATABASE {destination} SET search_path = actual_state,public")
    )
    await superuser.execute(
        text(f"ALTER DATABASE {destination} SET datestyle to 'ISO, YMD'")
    )
    await superuser.execute(
        text(f"ALTER DATABASE {destination} SET intervalstyle to 'sql_standard'")
    )
    await superuser.execute(
        text(f"ALTER DATABASE {destination} SET time zone 'Europe/Copenhagen'")
    )
    # Allow connections again
    await _set_database_connectable(superuser, source, True)
    await _set_database_connectable(superuser, destination, True)


def _get_current_database(session: db.AsyncSession) -> str:
    return session.get_bind().engine.url.database


def _get_snapshot_database(session: db.AsyncSession) -> str:
    current_database = _get_current_database(session)
    return f"{current_database}_snapshot"


@router.post("/database/snapshot", status_code=HTTP_204_NO_CONTENT)
async def snapshot(session: depends.Session) -> None:
    """
    Snapshot the database.
    """
    logger.warning("Snapshotting database")
    async with superuser_connection(
        lora_get_settings()
    ) as superuser:  # pragma: no cover
        await copy_database(
            superuser,
            source=_get_current_database(session),
            destination=_get_snapshot_database(session),
        )


@router.post("/database/restore", status_code=HTTP_204_NO_CONTENT)
async def restore(session: depends.Session) -> None:
    """
    Restore database snapshot.
    """
    logger.warning("Restoring database")
    async with superuser_connection(
        lora_get_settings()
    ) as superuser:  # pragma: no cover
        await copy_database(
            superuser,
            source=_get_snapshot_database(session),
            destination=_get_current_database(session),
        )
    ConfiguredOrganisation.clear()
