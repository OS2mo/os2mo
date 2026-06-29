# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add policy_rule condition"""

# TODO: Before release, consider folding this into the prior policy migrations.

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "401749b213fe"
down_revision: str | Sequence[str] | None = "54bce9fff984"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("policy_rule", sa.Column("condition", sa.String(), nullable=True))
    # Extend the uniqueness to include the condition so the same (type, field)
    # may carry several conditions. NULLS NOT DISTINCT keeps unconditional rules
    # deduplicated (PostgreSQL >= 15).
    op.execute("ALTER TABLE policy_rule DROP CONSTRAINT uq_policy_rule")
    op.execute(
        "ALTER TABLE policy_rule ADD CONSTRAINT uq_policy_rule "
        "UNIQUE NULLS NOT DISTINCT (policy_fk, type, field, condition)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE policy_rule DROP CONSTRAINT uq_policy_rule")
    op.execute(
        "ALTER TABLE policy_rule ADD CONSTRAINT uq_policy_rule "
        "UNIQUE (policy_fk, type, field)"
    )
    op.drop_column("policy_rule", "condition")
