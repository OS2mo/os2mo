# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""add substitute_roles.

Revision ID: f3d769cdfafd
Revises: 9c3ee7c575c0
Create Date: 2020-12-10 16:51:40.028450
"""
from alembic import op

from mora.conf_db.alembic.helpers.new_defaults import add_default_fields
from mora.conf_db.alembic.helpers.new_defaults import remove_default_fields
from mora.conf_db.alembic.helpers.session import get_session
# revision identifiers, used by Alembic.

revision = "f3d769cdfafd"
down_revision = "9c3ee7c575c0"
branch_labels = None
depends_on = None

NEW_FIELDS = [("substitute_roles", "")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
