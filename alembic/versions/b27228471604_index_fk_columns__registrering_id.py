# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""index fk columns '*_registrering_id'"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "b27228471604"
down_revision: str | Sequence[str] | None = "initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("b27228471604_index_fk_columns__registrering_id__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("b27228471604_index_fk_columns__registrering_id__downgrade.sql")
