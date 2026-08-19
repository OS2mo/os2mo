# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Grant the policy mutators to the built-in "Policy Administrator" policy"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d3e4f5a6b7c8"
down_revision: str | Sequence[str] | None = "b1c2d3e4f5a6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The Public policy, as seeded by b5c6d7e8f9a0
PUBLIC_UUID = "a115ee17-9bac-5eed-0000-7075626c6963"
# The Policy Administrator policy, as seeded by b1c2d3e4f5a6
POLICYADMIN_UUID = "ded1ca7e-9bac-5eed-706f-6c61646d696e"

# Every write to a policy takes the same permission: whoever may declare a
# policy's actors and rules may grant themselves anything, so there is no
# privilege gradient to model between creating, editing and deleting one
POLICYADMIN_MUTATORS = [
    "policy_create",
    "policy_update",
    "policy_delete",
    "policy_actor_declare",
    "policy_actors_declare",
    "policy_actor_delete",
    "policy_rule_declare",
    "policy_rules_declare",
    "policy_rule_delete",
]
DECLARE_CONDITION = '"declare_policy" in token.roles'

# A rule's CEL expressions may name roles, settings and entity identifiers, so
# reading them takes the read grant. Until the mutators existed they were
# public: the only ways to a rule were already gated, and an ungranted field
# is denied to everyone. Mutator returns hand rules to declare-only callers,
# so the fields now gate on read_policy like the collection
READ_GATED_RULE_FIELDS = [
    ("PolicyRule", "condition"),
    ("PolicyRule", "filter"),
]
READ_CONDITION = '"read_policy" in token.roles'

policy_rule = sa.table(
    "policy_rule",
    sa.column("type", sa.String),
    sa.column("field", sa.String),
    sa.column("condition", sa.String),
    sa.column("filter", sa.String),
    sa.column("policy_fk", sa.Uuid),
)


def upgrade() -> None:
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": "Mutation",
                "field": field,
                "condition": DECLARE_CONDITION,
                "policy_fk": POLICYADMIN_UUID,
            }
            for field in POLICYADMIN_MUTATORS
        ],
    )
    op.execute(
        policy_rule.delete()
        .where(policy_rule.c.policy_fk == PUBLIC_UUID)
        .where(policy_rule.c.type == "PolicyRule")
        .where(policy_rule.c.field.in_(["condition", "filter"]))
    )
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": type,
                "field": field,
                "condition": READ_CONDITION,
                "filter": "",
                "policy_fk": POLICYADMIN_UUID,
            }
            for type, field in READ_GATED_RULE_FIELDS
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_rule.delete()
        .where(policy_rule.c.policy_fk == POLICYADMIN_UUID)
        .where(policy_rule.c.type == "Mutation")
        .where(policy_rule.c.field.in_(POLICYADMIN_MUTATORS))
    )
    op.execute(
        policy_rule.delete()
        .where(policy_rule.c.policy_fk == POLICYADMIN_UUID)
        .where(policy_rule.c.type == "PolicyRule")
        .where(policy_rule.c.field.in_(["condition", "filter"]))
    )
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": type,
                "field": field,
                "condition": "",
                "filter": "",
                "policy_fk": PUBLIC_UUID,
            }
            for type, field in READ_GATED_RULE_FIELDS
        ],
    )
