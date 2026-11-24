# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rename actor column to uuid"""

from collections.abc import Sequence

from alembic import op

revision: str = "d476d403bccc"
down_revision: str | Sequence[str] | None = "7ddc0a4f2b51"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("actor", "actor", new_column_name="uuid")


def downgrade() -> None:
    op.alter_column("actor", "uuid", new_column_name="actor")
