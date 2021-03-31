# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""show_seniority.

Revision ID: d879327dade8
Revises: 4b81d9a86c80
Create Date: 2021-03-31 12:33:30.208757
"""
from alembic import op

from mora.conf_db.alembic.helpers.new_defaults import (add_default_fields,
                                                       remove_default_fields)
from mora.conf_db.alembic.helpers.session import get_session

# revision identifiers, used by Alembic.
revision = 'd879327dade8'
down_revision = '43fef976e18f'
branch_labels = None
depends_on = None


NEW_FIELDS = [("show_seniority", "False")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
