# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add policy_actor table"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4bf31456c509"
down_revision: str | Sequence[str] | None = "426b7b762dae"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "policy_actor",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        # Actor attribute to match on: "uuid", "username" or "role".
        sa.Column("kind", sa.String(255), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column(
            "policy_fk",
            sa.Uuid,
            sa.ForeignKey("policy.id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("policy_actor")
