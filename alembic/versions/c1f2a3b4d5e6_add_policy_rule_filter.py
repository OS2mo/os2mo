# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add policy_rule filter"""

# TODO: Before release, consider folding this into the prior policy migrations.

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c1f2a3b4d5e6"
down_revision: str | Sequence[str] | None = "1daee268c74f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("policy_rule", sa.Column("filter", sa.String(), nullable=True))
    # Extend the uniqueness to include the filter so the same (type, field,
    # condition) may carry several entity filters. NULLS NOT DISTINCT keeps
    # filter-less rules deduplicated (PostgreSQL >= 15).
    op.execute("ALTER TABLE policy_rule DROP CONSTRAINT uq_policy_rule")
    op.execute(
        "ALTER TABLE policy_rule ADD CONSTRAINT uq_policy_rule "
        "UNIQUE NULLS NOT DISTINCT (policy_fk, type, field, condition, filter)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE policy_rule DROP CONSTRAINT uq_policy_rule")
    op.execute(
        "ALTER TABLE policy_rule ADD CONSTRAINT uq_policy_rule "
        "UNIQUE NULLS NOT DISTINCT (policy_fk, type, field, condition)"
    )
    op.drop_column("policy_rule", "filter")
