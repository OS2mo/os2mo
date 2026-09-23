# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Write the unconditional CEL condition as true"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "fe18e9f0f40e"
down_revision: str | Sequence[str] | None = "a2e4c7d15b93"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("condition", sa.Text),
)
policy_write_rule = sa.table(
    "policy_write_rule",
    sa.column("condition", sa.Text),
)


def upgrade() -> None:
    op.execute(
        policy_read_rule.update()
        .where(policy_read_rule.c.condition == "")
        .values(condition="true")
    )
    op.execute(
        policy_write_rule.update()
        .where(policy_write_rule.c.condition == "")
        .values(condition="true")
    )


def downgrade() -> None:
    op.execute(
        policy_read_rule.update()
        .where(policy_read_rule.c.condition == "true")
        .values(condition="")
    )
    op.execute(
        policy_write_rule.update()
        .where(policy_write_rule.c.condition == "true")
        .values(condition="")
    )
