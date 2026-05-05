# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Initial LoRa database schema (read from "db-dump.sql")

Revision ID: initial
Revises:
Create Date: 2022-02-01 16:54:19.119687
"""

import os

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "initial"
down_revision = None
branch_labels = None
depends_on = None


def downgrade() -> None:
    op.execute(text("drop schema if exists actual_state cascade"))


def upgrade() -> None:
    """
    These steps are also performed by the "mox-db-init" container. We perform them here
    as well as part of the setup/teardown process of each unittest.
    """
    database_name = op.get_bind().engine.url.database
    op.execute("create schema if not exists actual_state")
    op.execute('create extension if not exists "uuid-ossp" with schema actual_state')
    op.execute("create extension if not exists btree_gist with schema actual_state")
    op.execute("create extension if not exists pg_trgm with schema actual_state")
    op.execute(
        f"alter database {database_name} set search_path to actual_state, public"
    )
    # The database's new search path only affects new connections, but we want
    # the rest of this migration to use it too.
    op.execute("set search_path to actual_state, public")
    op.execute(f"alter database {database_name} set datestyle to 'ISO, YMD'")
    op.execute(f"alter database {database_name} set intervalstyle to 'sql_standard'")
    # These steps are required by the LoRa test suite, which assumes that
    # API responses will use the Copenhagen time zone.
    # TODO: Are we _really_ sure OS2mo does not assume the same as well?
    op.execute(f"alter database {database_name} set time zone 'Europe/Copenhagen'")

    initial_schema_path = os.path.join(os.path.dirname(__file__), "initial_schema.sql")
    with open(initial_schema_path) as initial_schema:
        op.execute(text(initial_schema.read()))
