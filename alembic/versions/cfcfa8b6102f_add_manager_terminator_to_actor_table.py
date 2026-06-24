# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add manager terminator to actor table"""

from collections.abc import Sequence

from alembic import op

revision: str = "cfcfa8b6102f"
down_revision: str | Sequence[str] | None = "aeb818ae64be"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO actor (name, actor) VALUES
            ('Manager Terminator', '3aca9ef1-baad-c0de-6d61-6e6167657274'),
            ('Xflow', '8f107777-baad-c0de-7866-6c6f77000000')
        ON CONFLICT (actor) DO NOTHING
        """
    )


def downgrade() -> None:
    pass
