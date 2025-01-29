# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""index fk columns '*_registrering_id'

Revision ID: b27228471604
Revises: initial
Create Date: 2022-04-05 11:05:57.832331
"""

from oio_rest.db.alembic_helpers import apply_sql_from_file

# revision identifiers, used by Alembic.
revision = "b27228471604"
down_revision = "initial"
branch_labels = None
depends_on = None


def upgrade():
    apply_sql_from_file("b27228471604_index_fk_columns__registrering_id__upgrade.sql")


def downgrade():
    apply_sql_from_file("b27228471604_index_fk_columns__registrering_id__downgrade.sql")
