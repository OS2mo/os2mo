# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Move the owner rules into the policy tables"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from alembic_helpers.owner_rules import OWNER_RULES

revision: str = "4b2d9e7a1c36"
down_revision: str | Sequence[str] | None = "b5332b0a9276"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OWNER_UUID = "de1e6a7e-9bac-5eed-0000-006f776e6572"

policy = sa.table(
    "policy",
    sa.column("pk", sa.Uuid),
    sa.column("name", sa.Text),
    sa.column("description", sa.Text),
    sa.column("active", sa.Boolean),
    sa.column("role", sa.Text),
    sa.column("managed", sa.Boolean),
)
policy_write_rule = sa.table(
    "policy_write_rule",
    sa.column("mutator", sa.Text),
    sa.column("condition", sa.Text),
    sa.column("graphql_version", sa.Integer),
    sa.column("policy_fk", sa.Uuid),
)


def upgrade() -> None:
    op.bulk_insert(
        policy,
        [
            {
                "pk": OWNER_UUID,
                "name": "Owner",
                "description": "Write access to what the caller owns",
                "active": True,
                "role": "owner",
                "managed": True,
            }
        ],
    )
    op.bulk_insert(
        policy_write_rule,
        [
            {
                "mutator": mutator,
                "condition": condition,
                # The rules were written against GraphQL Version 30
                "graphql_version": 30,
                "policy_fk": OWNER_UUID,
            }
            for mutator, condition in OWNER_RULES
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_write_rule.delete().where(policy_write_rule.c.policy_fk == OWNER_UUID)
    )
    op.execute(policy.delete().where(policy.c.pk == OWNER_UUID))
