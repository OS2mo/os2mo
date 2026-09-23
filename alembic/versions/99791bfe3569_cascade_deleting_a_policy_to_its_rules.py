# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Cascade deleting a policy to its rules"""

from collections.abc import Sequence

from alembic import op

revision: str = "99791bfe3569"
down_revision: str | Sequence[str] | None = "fe18e9f0f40e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def recreate_foreign_keys(ondelete: str | None) -> None:
    op.drop_constraint(
        constraint_name="policy_read_rule_policy_fk_fkey", table_name="policy_read_rule"
    )
    op.create_foreign_key(
        constraint_name="policy_read_rule_policy_fk_fkey",
        source_table="policy_read_rule",
        referent_table="policy",
        local_cols=["policy_fk"],
        remote_cols=["pk"],
        ondelete=ondelete,
    )
    op.drop_constraint(
        constraint_name="policy_read_rule_field_rule_fk_fkey",
        table_name="policy_read_rule_field",
    )
    op.create_foreign_key(
        constraint_name="policy_read_rule_field_rule_fk_fkey",
        source_table="policy_read_rule_field",
        referent_table="policy_read_rule",
        local_cols=["rule_fk"],
        remote_cols=["pk"],
        ondelete=ondelete,
    )
    op.drop_constraint(
        constraint_name="policy_write_rule_policy_fk_fkey",
        table_name="policy_write_rule",
    )
    op.create_foreign_key(
        constraint_name="policy_write_rule_policy_fk_fkey",
        source_table="policy_write_rule",
        referent_table="policy",
        local_cols=["policy_fk"],
        remote_cols=["pk"],
        ondelete=ondelete,
    )


def upgrade() -> None:
    recreate_foreign_keys(ondelete="CASCADE")


def downgrade() -> None:
    recreate_foreign_keys(ondelete=None)
