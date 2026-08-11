# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap the built-in "RBAC" policy"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from alembic_helpers.rbac_map import RBAC_MAP

revision: str = "d7e8f9a0b1c2"
down_revision: str | Sequence[str] | None = "e8f9a0b1c2d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


RBAC_UUID = "12bac000-9bac-5eed-0000-000052424143"

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

# RBAC: one rule per permission-gated (type, field), gated on the field's
# required RBAC role via `"<role>" in token.roles`
RBAC_RULES: list[tuple[str, str, str]] = [
    (type, field, f'"{role}" in token.roles')
    for (type, field), (role, _, _) in sorted(RBAC_MAP.items())
]


def upgrade() -> None:
    op.execute(
        policy.insert().values(
            id=RBAC_UUID,
            name="RBAC",
            description="Grants each field to actors holding that field's permission.",
            active=True,
        )
    )
    op.execute(policy_actor.insert().values(kind="all", policy_fk=RBAC_UUID))
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": type,
                "field": field,
                "condition": condition,
                "policy_fk": RBAC_UUID,
            }
            for type, field, condition in RBAC_RULES
        ],
    )


def downgrade() -> None:
    op.execute(policy_rule.delete().where(policy_rule.c.policy_fk == RBAC_UUID))
    op.execute(policy_actor.delete().where(policy_actor.c.policy_fk == RBAC_UUID))
    op.execute(policy.delete().where(policy.c.id == RBAC_UUID))
