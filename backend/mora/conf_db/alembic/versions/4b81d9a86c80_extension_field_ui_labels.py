# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""extension_field_ui_names.

Revision ID: 4b81d9a86c80
Revises: d80ed6f59597
Create Date: 2021-03-11 15:43:07.495180
"""
from alembic import op

from mora.conf_db.alembic.helpers.new_defaults import (add_default_fields,
                                                       remove_default_fields)
from mora.conf_db.alembic.helpers.session import get_session

# revision identifiers, used by Alembic.
revision = '4b81d9a86c80'
down_revision = 'd80ed6f59597'
branch_labels = None
depends_on = None


NEW_FIELDS = [("extension_field_ui_labels", "")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
