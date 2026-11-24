# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Rename actor name to username"""

from collections.abc import Sequence

from alembic import op

revision: str = "7ddc0a4f2b51"
down_revision: str | Sequence[str] | None = "f19cddb98f23"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("actor", "name", new_column_name="username")


def downgrade() -> None:
    op.alter_column("actor", "username", new_column_name="name")
