# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add explicit manager to engagement reader"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a495fe4cf82a"
down_revision: str | Sequence[str] | None = "726f6c656269"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"
COLLECTION = "Engagement"
FIELD = "explicit_manager"

policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("pk", sa.Uuid),
    sa.column("collection", sa.Text),
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
