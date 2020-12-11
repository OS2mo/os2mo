# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""user_key_in_search.

Revision ID: 52a970a92d7d
Revises: 30d2c9cb05c6
Create Date: 2020-12-15 14:02:25.184426
"""
from alembic import op

# revision identifiers, used by Alembic.
from mora.conf_db.alembic.helpers.new_defaults import (add_default_fields,
                                                       remove_default_fields)
from mora.conf_db.alembic.helpers.session import get_session

# revision identifiers, used by Alembic.
revision = '52a970a92d7d'
down_revision = '30d2c9cb05c6'
branch_labels = None
depends_on = None


NEW_FIELDS = [("show_user_key_in_search", "False")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
