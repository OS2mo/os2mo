# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Policy engine (PBAC) schema

Create the ``policy``, ``policy_actor`` and ``policy_rule`` tables backing the
policy-based access-control engine. The built-in policies are seeded by the
following migration.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "9f8e7d6c5b4a"
down_revision: str | Sequence[str] | None = "cfcfa8b6102f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "policy",
        sa.Column(
            "id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Whether the policy is in effect; a policy only grants access while active.
        sa.Column(
            "activated",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_table(
        "policy_actor",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        # Actor attribute to match on: "role" (a Keycloak token role) or "all".
        sa.Column("kind", sa.String(255), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("policy_fk", sa.Uuid, sa.ForeignKey("policy.id"), nullable=False),
        sa.UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_actor"),
    )
    op.create_table(
        "policy_rule",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        # GraphQL-native resource: a (type, field) pair. "type" is a GraphQL
        # type (a collection's object type, or "Query"/"Mutation"); "field" is a
        # field/mutator on it, or "*" for all fields.
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("field", sa.Text, nullable=False),
        sa.Column("policy_fk", sa.Uuid, sa.ForeignKey("policy.id"), nullable=False),
        sa.UniqueConstraint("policy_fk", "type", "field", name="uq_policy_rule"),
    )


def downgrade() -> None:
    op.drop_table("policy_rule")
    op.drop_table("policy_actor")
    op.drop_table("policy")
