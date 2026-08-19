# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add the policy API's public fields to the built-in "Public" policy"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from alembic_helpers.policy_api_fields import POLICY_API_FIELDS

revision: str = "c2d3e4f5a6b7"
down_revision: str | Sequence[str] | None = "a0b1c2d3e4f5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# The Public policy, as seeded by b5c6d7e8f9a0
PUBLIC_UUID = "a115ee17-9bac-5eed-0000-7075626c6963"

policy_rule = sa.table(
    "policy_rule",
    sa.column("type", sa.String),
    sa.column("field", sa.String),
    sa.column("condition", sa.String),
    sa.column("filter", sa.String),
    sa.column("policy_fk", sa.Uuid),
)


# A rule's CEL expressions are public for now: the only ways to a rule are the
# two gated entry points, and an ungranted field is denied to everyone. The
# mutator migration gates them on read_policy once mutation returns hand rules
# to declare-only callers
PUBLIC_RULE_EXPRESSIONS = [
    ("PolicyRule", "condition"),
    ("PolicyRule", "filter"),
]


def upgrade() -> None:
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
            for type, field in sorted(POLICY_API_FIELDS | set(PUBLIC_RULE_EXPRESSIONS))
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_rule.delete()
        .where(policy_rule.c.policy_fk == PUBLIC_UUID)
        .where(
            sa.tuple_(policy_rule.c.type, policy_rule.c.field).in_(
                sorted(POLICY_API_FIELDS)
            )
        )
    )
