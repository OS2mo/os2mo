# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""drop unused indexes

Revision ID: 05765df45c68
Revises: b27228471604
Create Date: 2022-04-08 17:57:45.439305
"""

from oio_rest.db.alembic_helpers import apply_sql_from_file

# revision identifiers, used by Alembic.
revision = "05765df45c68"
down_revision = "b27228471604"
branch_labels = None
depends_on = None


def upgrade():
    apply_sql_from_file("05765df45c68_drop_unused_indexes__upgrade.sql")


def downgrade():
    apply_sql_from_file("05765df45c68_drop_unused_indexes__downgrade.sql")
