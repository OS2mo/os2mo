# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""make active_tils NOT NULL

The background job released alongside ``e2a9c47f1b6d`` has filled every existing
row, so the column can be made NOT NULL and the job retired. The BEFORE trigger
fills new rows synchronously at INSERT, so no DEFAULT is needed and ``SET NOT
NULL`` only scans to verify.

That assumes the release carrying ``e2a9c47f1b6d`` ran long enough for the job to
finish. A database crossing both migrations in one upgrade never gave it a
chance, so each ``SET NOT NULL`` is preceded by a no-op UPDATE that fills
whatever is left: slow rather than broken.
"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "b4e8d2f16a3c"
down_revision: str | Sequence[str] | None = "e2a9c47f1b6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("b4e8d2f16a3c_aktiv_virkning_not_null__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("b4e8d2f16a3c_aktiv_virkning_not_null__downgrade.sql")
