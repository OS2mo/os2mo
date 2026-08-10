# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap the built-in "Public" policy"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from alembic_helpers.public_fields import PUBLIC_FIELDS

revision: str = "b5c6d7e8f9a0"
down_revision: str | Sequence[str] | None = "9f8e7d6c5b4a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PUBLIC_UUID = "a115ee17-9bac-5eed-0000-7075626c6963"

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
            id=PUBLIC_UUID,
            name="Public",
            description="Grants access to public fields",
            active=True,
        )
    )
    op.execute(policy_actor.insert().values(kind="all", policy_fk=PUBLIC_UUID))
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": type,
                "field": field,
                "policy_fk": PUBLIC_UUID,
            }
            for type, field in sorted(PUBLIC_FIELDS)
        ],
    )


def downgrade() -> None:
    op.execute(policy_rule.delete().where(policy_rule.c.policy_fk == PUBLIC_UUID))
    op.execute(policy_actor.delete().where(policy_actor.c.policy_fk == PUBLIC_UUID))
    op.execute(policy.delete().where(policy.c.id == PUBLIC_UUID))
