# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""show_owner.

Revision ID: 80ad47778b09
Revises: d879327dade8
Create Date: 2021-04-28 14:04:33.725858
"""
from alembic import op

from mora.conf_db.alembic.helpers.new_defaults import add_default_fields
from mora.conf_db.alembic.helpers.new_defaults import remove_default_fields
from mora.conf_db.alembic.helpers.session import get_session

# revision identifiers, used by Alembic.

revision = "80ad47778b09"
down_revision = "d879327dade8"
branch_labels = None
depends_on = None

NEW_FIELDS = [("show_owner", "False")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
