# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""remove integrationsdata

Revision ID: b162ba90c028
Revises: b27228471604
Create Date: 2022-06-28 14:06:39.199705
"""

from oio_rest.db.alembic_helpers import apply_sql_from_file

# revision identifiers, used by Alembic.
revision = "b162ba90c028"
down_revision = "b27228471604"
branch_labels = None
depends_on = None


def upgrade():
    apply_sql_from_file("b162ba90c028_remove_integrationsdata__upgrade.sql")


def downgrade():
    apply_sql_from_file("b162ba90c028_remove_integrationsdata__downgrade.sql")
