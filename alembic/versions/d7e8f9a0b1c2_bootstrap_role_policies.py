# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap the built-in "Reader" and "Admin" policies"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from alembic_helpers.rbac_map import RBAC_MAP

revision: str = "d7e8f9a0b1c2"
down_revision: str | Sequence[str] | None = "e8f9a0b1c2d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


READER_UUID = "12bac000-9bac-5eed-0000-726561646572"
ADMIN_UUID = "12bac000-9bac-5eed-0000-000061646d69"

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

POLICIES = {
    READER_UUID: (
        "Reader",
        "Grants each read field to actors holding the reader role.",
    ),
    ADMIN_UUID: (
        "Admin",
        "Grants each write field to actors holding the admin role.",
    ),
}

# One rule per permission-gated (type, field), gated on the field's required
# role via `"<role>" in token.roles`, split into a policy per role
RULES: dict[str, list[tuple[str, str, str]]] = {
    uuid: [
        (type, field, f'"{role}" in token.roles')
        for (type, field), role in sorted(RBAC_MAP.items())
        if ("reader" if uuid == READER_UUID else "admin") == role
    ]
    for uuid in POLICIES
}


def upgrade() -> None:
    for uuid, (name, description) in POLICIES.items():
        op.execute(
            policy.insert().values(
                id=uuid,
                name=name,
                description=description,
                active=True,
            )
        )
        op.execute(policy_actor.insert().values(kind="all", policy_fk=uuid))
        op.bulk_insert(
            policy_rule,
            [
                {
                    "type": type,
                    "field": field,
                    "condition": condition,
                    "policy_fk": uuid,
                }
                for type, field, condition in RULES[uuid]
            ],
        )


def downgrade() -> None:
    for uuid in POLICIES:
        op.execute(policy_rule.delete().where(policy_rule.c.policy_fk == uuid))
        op.execute(policy_actor.delete().where(policy_actor.c.policy_fk == uuid))
        op.execute(policy.delete().where(policy.c.id == uuid))
