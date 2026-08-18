# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add relation reg_rel indexes"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "d903192968e9"
down_revision: str | Sequence[str] | None = "b4e8d2f16a3c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("d903192968e9_add_relation_reg_rel_indexes__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("d903192968e9_add_relation_reg_rel_indexes__downgrade.sql")
