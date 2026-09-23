# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Let a policy be managed"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b5332b0a9276"
down_revision: str | Sequence[str] | None = "99791bfe3569"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"

policy = sa.table(
    "policy",
    sa.column("pk", sa.Uuid),
    sa.column("managed", sa.Boolean),
)


def upgrade() -> None:
    op.add_column(
        "policy",
        sa.Column("managed", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    # The migrations seed the Reader policy, and keep managing it
    op.execute(
        policy.update().where(policy.c.pk == READER_UUID).values(managed=sa.true())
    )


def downgrade() -> None:
    op.drop_column("policy", "managed")
