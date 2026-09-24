# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Let a selector take no value"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "8b21d6f4c0a7"
down_revision: str | Sequence[str] | None = "5e0c7a4f2d19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

policy_selector = sa.table(
    "policy_selector",
    sa.column("kind", postgresql.ENUM(name="policyselectorkind", create_type=False)),
    sa.column("value", sa.Text),
)


def recreate_unique_constraint(nulls_not_distinct: bool) -> None:
    op.drop_constraint(
        constraint_name="uq_policy_selector", table_name="policy_selector"
    )
    op.create_unique_constraint(
        constraint_name="uq_policy_selector",
        table_name="policy_selector",
        columns=["policy_fk", "kind", "value"],
        postgresql_nulls_not_distinct=nulls_not_distinct,
    )


def upgrade() -> None:
    op.execute("ALTER TYPE policyselectorkind ADD VALUE IF NOT EXISTS 'all'")
    op.alter_column("policy_selector", "value", nullable=True)
    # Two selectors taking no value are as alike as two taking the same one
    recreate_unique_constraint(nulls_not_distinct=True)


def downgrade() -> None:
    # The previous revision knows neither the all kind nor selectors taking no value
    op.execute(
        policy_selector.delete().where(
            sa.or_(policy_selector.c.kind == "all", policy_selector.c.value.is_(None))
        )
    )
    recreate_unique_constraint(nulls_not_distinct=False)
    op.alter_column("policy_selector", "value", nullable=False)
    # Postgres cannot drop a value from an enum, so `all` is left in the type
