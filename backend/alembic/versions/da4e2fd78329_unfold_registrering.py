# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""unfold registrering composite into separate columns"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "da4e2fd78329"
down_revision: str | Sequence[str] | None = "aeb818ae64be"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("da4e2fd78329_unfold_registrering__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("da4e2fd78329_unfold_registrering__downgrade.sql")
