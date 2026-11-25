# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add hardcoded actors to actor table"""

from collections.abc import Sequence

from alembic import op

revision: str = "6163746f7273"
down_revision: str | Sequence[str] | None = "66696c65735f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO actor (name, actor) VALUES
            ('Auth disabled', '00000000-0000-0000-0000-000000000000'),
            ('Legacy auth', '00000000-0000-0000-0000-000000000001')
        ON CONFLICT (actor) DO NOTHING
        """
    )


def downgrade() -> None:
    pass
