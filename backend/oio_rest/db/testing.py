# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os

from psycopg2.errors import OperationalError
from psycopg2.errors import UndefinedTable
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from . import get_connection
from .. import config
from .alembic_helpers import get_alembic_cfg
from .alembic_helpers import get_prerequisites
from .alembic_helpers import is_schema_installed
from .alembic_helpers import setup_database
from .alembic_helpers import stamp_database
from .alembic_helpers import truncate_all_tables
from alembic import command


def ensure_testing_database_exists():
    settings = config.get_settings()
    non_test_dbname = settings.db_name

    _begin_or_continue_testing()

    with get_connection(dbname=non_test_dbname) as connection:
        with connection.cursor() as cursor:
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            _terminate_connections(cursor, "mox_test")
            try:
                # try and get a connection to mox_test
                get_connection()
            except OperationalError:
                # could not get a connection to mox_test; create new db
                cursor.execute("create database mox_test owner mox encoding utf8")
                for prerequisite in get_prerequisites(db_name="mox_test"):
                    cursor.execute(prerequisite)
    # Install "actual_state" schema in testing database
    setup_testing_database()


def setup_testing_database():
    """Install "actual_state" schema in testing database"""

    _check_current_database_is_testing()

    if is_schema_installed():
        # Truncate all tables in the "actual_state" schema
        reset_testing_database()
        # Sometimes the LoRa schema "actual_state" is present, but the
        # Alembic migrations table is not ("public.alembic_version".)
        # In such cases, we stamp the database as migrated by Alembic.
        if not _is_alembic_installed():
            stamp_database()
    else:
        # Initialise "actual_state" schema
        setup_database()


def reset_testing_database():
    """Truncate all tables in the 'actual_state' schema, in the testing database"""

    _begin_or_continue_testing()
    _check_current_database_is_testing()
    truncate_all_tables()


def teardown_testing_database():
    """Remove "actual_state" schema from testing database"""

    _begin_or_continue_testing()
    _check_current_database_is_testing()
    command.downgrade(get_alembic_cfg(), "base")
    stop_testing()


def _begin_or_continue_testing():
    os.environ["TESTING"] = "True"


def stop_testing():
    os.environ.pop("TESTING", None)


def get_testing() -> bool:
    return os.environ.get("TESTING", "") == "True"


def _check_current_database_is_testing():
    # Check that we are operating on the testing database
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute("select current_database()")
        current_database = cursor.fetchone()[0]
        assert current_database.endswith("_test")


def _is_alembic_installed() -> bool:
    query_migrations_applied = "select count(*) from alembic_version"
    with get_connection() as connection, connection.cursor() as cursor:
        try:
            cursor.execute(query_migrations_applied)
        except UndefinedTable:
            return False
        else:
            return cursor.fetchone()[0] > 0


def _terminate_connections(cursor, dbname):
    return cursor.execute(
        """
        select
            pg_terminate_backend(pid)
        from
            pg_stat_activity
        where
            datname = %s
            and
            pid <> pg_backend_pid()
        """,
        (dbname,),
    )
