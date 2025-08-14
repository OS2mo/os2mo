# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add file_tokens"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

revision: str = "699bd68b7e73"
down_revision: str | Sequence[str] | None = "03ba622eeeb3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "file_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, default=func.now()
        ),
        sa.Column("secret", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("file_tokens")
