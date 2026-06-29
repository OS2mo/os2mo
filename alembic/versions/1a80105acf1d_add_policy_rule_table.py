# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add policy_rule table"""

# TODO: Before release, merge this migration into the prior policy migrations
# so policies ship as a single migration rather than this incremental dev
# history.

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "1a80105acf1d"
down_revision: str | Sequence[str] | None = "4bf31456c509"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Magic UUID; keep in sync with mora.db.policies.POLICYADMIN_UUID.
POLICYADMIN_UUID = "ded1ca7e-9bac-5eed-706f-6c61646d696e"

# Rules giving the bootstrap Policy Administrator access to manage policies, so
# the admin role can administer the policy system when PBAC is enabled. These
# rules (like the policy) are protected from modification.
POLICYADMIN_RULES = [
    ("Query", "policies"),
    ("Mutation", "policy_declare"),
    ("Mutation", "policy_delete"),
    ("Mutation", "policy_actor_declare"),
    ("Mutation", "policy_actors_declare"),
    ("Mutation", "policy_actor_delete"),
    ("Mutation", "policy_rule_declare"),
    ("Mutation", "policy_rules_declare"),
    ("Mutation", "policy_rule_delete"),
]


def upgrade() -> None:
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
        sa.Column(
            "policy_fk",
            sa.Uuid,
            sa.ForeignKey("policy.id"),
            nullable=False,
        ),
        # Makes `policy_rule_declare` idempotent.
        sa.UniqueConstraint("policy_fk", "type", "field", name="uq_policy_rule"),
    )

    values = ", ".join(
        f"('{type}', '{field}', '{POLICYADMIN_UUID}')"
        for type, field in POLICYADMIN_RULES
    )
    op.execute(f"INSERT INTO policy_rule (type, field, policy_fk) VALUES {values}")


def downgrade() -> None:
    op.drop_table("policy_rule")
