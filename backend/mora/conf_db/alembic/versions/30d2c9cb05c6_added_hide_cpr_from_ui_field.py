# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""added_hide_cpr_from_ui_field.

Revision ID: 30d2c9cb05c6
Revises: f3d769cdfafd
Create Date: 2020-12-11 09:16:22.469457
"""
from alembic import op

# revision identifiers, used by Alembic.
from mora.conf_db.alembic.helpers.new_defaults import (add_default_fields,
                                                       remove_default_fields)
from mora.conf_db.alembic.helpers.session import get_session

# revision identifiers, used by Alembic.
revision = '30d2c9cb05c6'
down_revision = 'f3d769cdfafd'
branch_labels = None
depends_on = None

NEW_FIELDS = [("show_cpr_no", "True")]


def upgrade():
    """Insert missing default settings, if any"""
    bind = op.get_bind()
    with get_session(bind) as session:
        add_default_fields(session, NEW_FIELDS)


def downgrade():
    bind = op.get_bind()
    with get_session(bind) as session:
        remove_default_fields(session, NEW_FIELDS)
