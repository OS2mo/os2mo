# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Let a policy be switched off"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a17c3f9e2b41"
down_revision: str | Sequence[str] | None = "b93e5c17af08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

policy = sa.table(
    "policy",
    sa.column("active", sa.Boolean),
)


def upgrade() -> None:
    op.add_column("policy", sa.Column("active", sa.Boolean))
    # The policies already in the table are in use, so they are active
    op.execute(policy.update().values(active=sa.true()))
    op.alter_column("policy", "active", nullable=False)


def downgrade() -> None:
    op.drop_column("policy", "active")
