# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add primary to manager reader"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b45b3fbb0cbf"
down_revision: str | Sequence[str] | None = "5e0c7a4f2d19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"
COLLECTION = "Manager"
FIELD = "primary_response"

policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("pk", sa.Uuid),
    sa.column(
        "collection", postgresql.ENUM(name="policycollection", create_type=False)
    ),
    sa.column("policy_fk", sa.Uuid),
)
policy_read_rule_field = sa.table(
    "policy_read_rule_field",
    sa.column("field", sa.Text),
    sa.column("rule_fk", sa.Uuid),
)


def upgrade() -> None:
    # The Reader policy is the one the migrations seed and keep managing
    op.execute(
        policy_read_rule_field.insert().from_select(
            ["field", "rule_fk"],
            sa.select(sa.literal(FIELD), policy_read_rule.c.pk).where(
                policy_read_rule.c.collection == COLLECTION,
                policy_read_rule.c.policy_fk == READER_UUID,
            ),
        )
    )


def downgrade() -> None:
    op.execute(
        policy_read_rule_field.delete().where(
            policy_read_rule_field.c.field == FIELD,
            policy_read_rule_field.c.rule_fk.in_(
                sa.select(policy_read_rule.c.pk).where(
                    policy_read_rule.c.collection == COLLECTION,
                    policy_read_rule.c.policy_fk == READER_UUID,
                )
            ),
        )
    )
