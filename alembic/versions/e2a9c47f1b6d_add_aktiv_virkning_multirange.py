# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add active_tils multirange to relation/attr tables

Adds ``active_tils``, its two maintenance triggers and the expression GiST index
on the overlap.

Added NULLable and deliberately not backfilled here, because touching every row
in one migration is too slow online: ``mora.db.backfill`` fills existing rows and
``b4e8d2f16a3c`` makes the column NOT NULL once it has.
"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "e2a9c47f1b6d"
down_revision: str | Sequence[str] | None = "a4e0c9b7d312"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("e2a9c47f1b6d_add_aktiv_virkning_multirange__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("e2a9c47f1b6d_add_aktiv_virkning_multirange__downgrade.sql")
