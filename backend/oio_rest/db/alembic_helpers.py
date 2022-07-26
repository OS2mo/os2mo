# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
from typing import List

from psycopg2.errors import UndefinedTable

from . import get_connection
from alembic import command
from alembic.config import Config


def get_alembic_cfg() -> Config:
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    default_path = os.path.join(base_dir, "alembic.ini")
    alembic_cfg_path = os.environ.get("ALEMBIC_CONFIG", default_path)
    alembic_cfg = Config(alembic_cfg_path)
    return alembic_cfg


def is_schema_installed() -> bool:
    "Return True if LoRa database schema is already installed"
    query_schema_installed = "select 1 from actual_state.bruger limit 1"
    with get_connection() as connection, connection.cursor() as cursor:
        try:
            cursor.execute(query_schema_installed)
        except UndefinedTable:
            return False
        else:
            return True


def get_prerequisites(
    schema_name="actual_state", db_user="mox", db_name="mox"
) -> List[str]:
    return [
        # These steps are also performed by the "mox-db-init" container.
        # We perform them here as well as part of the setup/teardown process of
        # each unittest.
        f"create schema if not exists {schema_name} authorization {db_user}",
        f'create extension if not exists "uuid-ossp" with schema {schema_name}',
        f"create extension if not exists btree_gist with schema {schema_name}",
        f"create extension if not exists pg_trgm with schema {schema_name}",
        f"alter database {db_name} set search_path to {schema_name}, public",
        f"alter database {db_name} set datestyle to 'ISO, YMD'",
        f"alter database {db_name} set intervalstyle to 'sql_standard'",
        # These steps are required by the LoRa test suite, which assumes that
        # API responses will use the Copenhagen time zone.
        f"alter database {db_name} set time zone 'Europe/Copenhagen'",
        "set time zone 'Europe/Copenhagen'",
    ]


def stamp_database():
    # Apply fake Alembic migrations, reflecting the legacy schema
    return command.stamp(get_alembic_cfg(), "initial")


def setup_database():
    return command.upgrade(get_alembic_cfg(), "head")


def truncate_all_tables():
    """Truncate all tables in the 'actual_state' schema"""

    schema_name = "actual_state"
    truncate_all = """
        do
        $func$
        begin
        execute (
            select
                'truncate table ' || string_agg(oid::regclass::text, ', ') || ' cascade'
            from
                pg_class
            where
                relkind = 'r'  -- only tables
                and
                relnamespace = %s::regnamespace
        );
        end
        $func$;
    """
    with get_connection() as connection, connection.cursor() as cursor:
        return cursor.execute(truncate_all, (schema_name,))
