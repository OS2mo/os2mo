# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""deprecate read_only.

Revision ID: d80ed6f59597
Revises: 52a970a92d7d
Create Date: 2021-02-17 15:10:08.227829
"""
from alembic import op

from mora.conf_db.alembic.helpers.new_defaults import add_default_fields
from mora.conf_db.alembic.helpers.new_defaults import remove_default_fields
from mora.conf_db.alembic.helpers.session import get_session
# revision identifiers, used by Alembic.

revision = "d80ed6f59597"
down_revision = "52a970a92d7d"
branch_labels = None
depends_on = None

DEPRECATE_FIELDS = [("read_only", "False")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, DEPRECATE_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, DEPRECATE_FIELDS)
