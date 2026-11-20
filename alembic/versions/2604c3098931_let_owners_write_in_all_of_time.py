# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Let owners write what they own in all of time

The owner rules looked up what a mutator names, and the hierarchy linking it to
what the caller owns, as of today only. An owner could therefore not write the
past or the future of what they own, e.g. a unit that only comes into existence
next month. Whether the caller is an owner is still decided as of today, since
`owner_filter` is left untouched, but what they own is now looked up in all of
time.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "2604c3098931"
down_revision: str | Sequence[str] | None = "66696c65735f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OWNER_UUID = "de1e6a7e-9bac-5eed-0000-006f776e6572"

policy_write_rule = sa.table(
    "policy_write_rule",
    sa.column("pk", sa.Uuid),
    sa.column("condition", sa.Text),
    sa.column("policy_fk", sa.Uuid),
)

# Every filter of the owner rules naming what is owned, or how it is linked to
# what is owned. The owner filter itself is bound as `owner_filter`, and never
# opened by any of these keys, so it keeps looking at today only.
KEYS = ("filter", "descendant", "ancestor", "child", "org_unit", "employee")
ALL_OF_TIME = '"from_date": null, "to_date": null, '


def _rewrite(old: str, new: str) -> None:
    connection = op.get_bind()
    rules = connection.execute(
        sa.select(policy_write_rule.c.pk, policy_write_rule.c.condition).where(
            policy_write_rule.c.policy_fk == OWNER_UUID
        )
    ).all()
    for pk, condition in rules:
        for key in KEYS:
            condition = condition.replace(old.format(key=key), new.format(key=key))
        connection.execute(
            policy_write_rule.update()
            .where(policy_write_rule.c.pk == pk)
            .values(condition=condition)
        )


def upgrade() -> None:
    _rewrite('"{key}": {{', '"{key}": {{' + ALL_OF_TIME)


def downgrade() -> None:
    _rewrite('"{key}": {{' + ALL_OF_TIME, '"{key}": {{')
