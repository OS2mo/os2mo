# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from more_itertools import one
from psycopg2.errors import UndefinedTable
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from oio_rest import config
from oio_rest.db import close_connection
from oio_rest.db import get_connection
from oio_rest.db import get_new_connection
from oio_rest.db.alembic_helpers import get_prerequisites
from oio_rest.db.alembic_helpers import is_schema_installed
from oio_rest.db.alembic_helpers import setup_database
from oio_rest.db.alembic_helpers import stamp_database
from oio_rest.db.alembic_helpers import truncate_all_tables


def create_new_testing_database(identifier: str) -> str:
    settings = config.get_settings()
    non_test_dbname = settings.db_name

    new_db_name = "_".join([non_test_dbname, identifier, "test"])

    try:
        connection = get_new_connection()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS {new_db_name}")
            cursor.execute(f"CREATE DATABASE {new_db_name} OWNER mox")
            for prerequisite in get_prerequisites(db_name=new_db_name):
                cursor.execute(prerequisite)
    finally:
        close_connection()

    return new_db_name


def setup_testing_database() -> None:
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


def reset_testing_database() -> None:
    """Truncate all tables in the 'actual_state' schema, in the testing database"""
    # HACK as long as we have two ways to generate sample structure data
    # the are_fixtures_loaded needs to be set to false to ensure
    # the correct change between minimal and full sample structure data

    _check_current_database_is_testing()
    truncate_all_tables()


def remove_testing_database(new_db_name: str) -> None:
    """Remove the testing database entirely"""
    try:
        connection = get_new_connection()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            # Forcefully terminate all connections to the database
            cursor.execute(
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
                (new_db_name,),
            )
            # Drop the database
            cursor.execute(f"DROP DATABASE {new_db_name}")
    finally:
        close_connection()


def _check_current_database_is_testing() -> None:
    # Check that we are operating on the testing database
    with get_connection().cursor() as cursor:
        cursor.execute("select current_database()")
        current_database = one(cursor.fetchone())
        assert current_database.endswith("_test")


def _is_alembic_installed() -> bool:
    query_migrations_applied = "select count(*) from alembic_version"
    with get_connection().cursor() as cursor:
        try:
            cursor.execute(query_migrations_applied)
        except UndefinedTable:
            return False
        else:
            return one(cursor.fetchone()) > 0
