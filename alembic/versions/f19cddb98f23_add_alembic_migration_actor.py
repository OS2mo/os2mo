# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add Alembic migration actor to actor table"""

from collections.abc import Sequence

from alembic import op

revision: str = "f19cddb98f23"
down_revision: str | Sequence[str] | None = "68559a270001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO actor (name, actor)
        VALUES ('Alembic migration', 'a1e11b1c-baad-c0de-1337-a4e0c9b7d312')
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    pass
