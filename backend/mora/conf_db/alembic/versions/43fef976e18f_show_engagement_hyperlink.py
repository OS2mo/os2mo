# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""show_engagement_hyperlink.

Revision ID: 43fef976e18f
Revises: d80ed6f59597
Create Date: 2021-03-16 14:50:32.842955
"""
from alembic import op

from mora.conf_db.alembic.helpers.new_defaults import add_default_fields
from mora.conf_db.alembic.helpers.new_defaults import remove_default_fields
from mora.conf_db.alembic.helpers.session import get_session

# revision identifiers, used by Alembic.
revision = "43fef976e18f"
down_revision = "4b81d9a86c80"
branch_labels = None
depends_on = None

NEW_FIELDS = [("show_engagement_hyperlink", "False")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
