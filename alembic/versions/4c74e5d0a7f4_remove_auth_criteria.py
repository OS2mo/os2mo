# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""remove auth criteria"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "4c74e5d0a7f4"
down_revision: str | Sequence[str] | None = "d903192968e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("4c74e5d0a7f4_remove_auth_criteria__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("4c74e5d0a7f4_remove_auth_criteria__downgrade.sql")
