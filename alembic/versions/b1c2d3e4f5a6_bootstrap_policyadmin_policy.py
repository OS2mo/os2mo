# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap the built-in "Policy Administrator" policy"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: str | Sequence[str] | None = "c2d3e4f5a6b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


POLICYADMIN_UUID = "ded1ca7e-9bac-5eed-706f-6c61646d696e"

policy_actor_kind = postgresql.ENUM(
    "role",
    "all",
    name="policy_actor_kind",
    # Avoid implicit creation
    create_type=False,
)
policy = sa.table(
    "policy",
    sa.column("id", sa.Uuid),
    sa.column("name", sa.String),
    sa.column("description", sa.String),
    sa.column("active", sa.Boolean),
)
policy_actor = sa.table(
    "policy_actor",
    sa.column("kind", policy_actor_kind),
    sa.column("value", sa.String),
    sa.column("policy_fk", sa.Uuid),
)
policy_rule = sa.table(
    "policy_rule",
    sa.column("type", sa.String),
    sa.column("field", sa.String),
    sa.column("condition", sa.String),
    sa.column("policy_fk", sa.Uuid),
)

POLICYADMIN_RULES = [
    ("Myself", "policies", "read_policy"),
    ("Query", "policies", "read_policy"),
]


def upgrade() -> None:
    op.execute(
        policy.insert().values(
            id=POLICYADMIN_UUID,
            name="Policy Administrator",
            description="Grants the policy API to actors holding its permission.",
            active=True,
        )
    )
    op.execute(policy_actor.insert().values(kind="all", policy_fk=POLICYADMIN_UUID))
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": type,
                "field": field,
                "condition": f'"{role}" in token.roles',
                "policy_fk": POLICYADMIN_UUID,
            }
            for type, field, role in POLICYADMIN_RULES
        ],
    )


def downgrade() -> None:
    op.execute(policy_rule.delete().where(policy_rule.c.policy_fk == POLICYADMIN_UUID))
    op.execute(
        policy_actor.delete().where(policy_actor.c.policy_fk == POLICYADMIN_UUID)
    )
    op.execute(policy.delete().where(policy.c.id == POLICYADMIN_UUID))
