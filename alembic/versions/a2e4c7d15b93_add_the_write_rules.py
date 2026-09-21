# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add the write rules"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a2e4c7d15b93"
down_revision: str | Sequence[str] | None = "c81f4a2d0b7e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "policy_write_rule",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("mutator", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=False),
        sa.Column("graphql_version", sa.Integer, nullable=False),
        sa.Column("policy_fk", sa.Uuid, sa.ForeignKey("policy.pk"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("policy_write_rule")
