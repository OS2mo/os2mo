# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Initial LoRa database schema (read from "db-dump.sql")

Revision ID: initial
Revises:
Create Date: 2022-02-01 16:54:19.119687
"""
import os

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from alembic import op
from oio_rest import config
from oio_rest.db.alembic_helpers import get_prerequisites

# revision identifiers, used by Alembic.
revision = "initial"
down_revision = None
branch_labels = None
depends_on = None


Session = sessionmaker()

schema_name = "actual_state"


def downgrade():
    drop_schema = text(f"drop schema if exists {schema_name} cascade")
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(drop_schema)


def upgrade():
    settings = config.get_settings()

    prerequisites = get_prerequisites(
        schema_name=schema_name,
        db_user=settings.db_user,
        db_name=settings.db_name,
    )

    initial_schema_path = os.path.join(os.path.dirname(__file__), "initial_schema.sql")

    bind = op.get_bind()
    session = Session(bind=bind)

    for prerequisite in prerequisites:
        session.execute(text(prerequisite))

    with open(initial_schema_path) as initial_schema:
        session.execute(
            text(initial_schema.read().replace("{{ mox_user }}", settings.db_user))
        )
