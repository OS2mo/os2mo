# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Policy engine (PBAC) schema"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "9f8e7d6c5b4a"
down_revision: str | Sequence[str] | None = "b4e8d2f16a3c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


policy_actor_kind = postgresql.ENUM(
    "role",
    "all",
    name="policy_actor_kind",
    # Avoid implicit creation
    create_type=False,
)


def upgrade() -> None:
    policy_actor_kind.create(op.get_bind())

    op.create_table(
        "policy",
        sa.Column(
            "id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.func.uuid_generate_v4(),
        ),
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text,
            nullable=False,
            server_default="",
        ),
        sa.Column(
            "active",
            sa.Boolean,
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "policy_actor",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.func.uuid_generate_v4(),
        ),
        sa.Column(
            "policy_fk",
            sa.Uuid,
            sa.ForeignKey("policy.id"),
            nullable=False,
        ),
        sa.Column(
            "kind",
            policy_actor_kind,
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Text,
            nullable=False,
            server_default="",
        ),
        sa.CheckConstraint(
            "kind = 'all' OR value <> ''",
            name="ck_policy_actor_value",
        ),
        sa.UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_actor"),
    )

    op.create_table(
        "policy_rule",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.func.uuid_generate_v4(),
        ),
        sa.Column(
            "policy_fk",
            sa.Uuid,
            sa.ForeignKey("policy.id"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Text,
            nullable=False,
        ),
        sa.Column(
            "field",
            sa.Text,
            nullable=False,
        ),
        sa.UniqueConstraint("policy_fk", "type", "field", name="uq_policy_rule"),
    )


def downgrade() -> None:
    op.drop_table("policy_rule")
    op.drop_table("policy_actor")
    op.drop_table("policy")
    policy_actor_kind.drop(op.get_bind())
