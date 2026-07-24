# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap the built-in "Introspection" policy"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from alembic_helpers.introspection import INTROSPECTION_RULES

revision: str = "c6d7e8f9a0b1"
down_revision: str | Sequence[str] | None = "b5c6d7e8f9a0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


INTROSPECTION_UUID = "5e1fde5c-9bac-5eed-696e-74726f737065"

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
    sa.column("policy_fk", sa.Uuid),
)


def upgrade() -> None:
    op.execute(
        policy.insert().values(
            id=INTROSPECTION_UUID,
            name="Introspection",
            description="Grants GraphQL introspection access to every actor.",
            active=True,
        )
    )
    op.execute(policy_actor.insert().values(kind="all", policy_fk=INTROSPECTION_UUID))
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": type,
                "field": field,
                "policy_fk": INTROSPECTION_UUID,
            }
            for type, field in sorted(INTROSPECTION_RULES)
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_rule.delete().where(policy_rule.c.policy_fk == INTROSPECTION_UUID)
    )
    op.execute(
        policy_actor.delete().where(policy_actor.c.policy_fk == INTROSPECTION_UUID)
    )
    op.execute(policy.delete().where(policy.c.id == INTROSPECTION_UUID))
