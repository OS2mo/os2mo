# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add the policy tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a3d1c7e05f24"
down_revision: str | Sequence[str] | None = "d903192968e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


policy_selector_kind = postgresql.ENUM(
    "role",
    "all",
    name="policy_selector_kind",
    # Avoid implicit creation
    create_type=False,
)


def upgrade() -> None:
    policy_selector_kind.create(op.get_bind())

    op.create_table(
        "policy",
        sa.Column(
            "id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_table(
        "policy_selector",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("kind", policy_selector_kind, nullable=False),
        sa.Column("value", sa.Text, nullable=False, server_default=""),
        sa.Column("policy_fk", sa.Uuid, sa.ForeignKey("policy.id"), nullable=False),
        sa.CheckConstraint(
            "kind = 'all' OR value <> ''", name="ck_policy_selector_value"
        ),
        sa.UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_selector"),
    )
    op.create_table(
        "policy_mutator",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=False, server_default=""),
        sa.Column("filter", sa.Text, nullable=False, server_default=""),
        sa.Column("policy_fk", sa.Uuid, sa.ForeignKey("policy.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("policy_mutator")
    op.drop_table("policy_selector")
    op.drop_table("policy")
    policy_selector_kind.drop(op.get_bind())
