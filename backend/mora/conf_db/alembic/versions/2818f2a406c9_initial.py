# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""Initial migration, noop on existing databases.

This introduces our ORM model to helpers/config_v1

Revision ID: 2818f2a406c9
Revises:
Create Date: 2020-11-13 15:00:01.575703
"""
from alembic import op
from mora.conf_db.alembic.helpers.config_v1 import Config
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "2818f2a406c9"
down_revision = None
branch_labels = None
depends_on = None


def db_table_exists(bind, tablename):
    """Check if a table with tablename exists."""
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()
    return tablename in tables


def upgrade():
    """Create Config table if non-existent, noop otherwise."""
    bind = op.get_bind()

    if db_table_exists(bind, Config.__tablename__):
        return
    Config.__table__.create(bind)


def downgrade():
    """Drop Config table."""
    op.drop_table(Config.__tablename__)
