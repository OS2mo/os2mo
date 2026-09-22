# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add CEL condition and GraphQL version to read rules"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c81f4a2d0b7e"
down_revision: str | Sequence[str] | None = "a17c3f9e2b41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("condition", sa.Text),
    sa.column("graphql_version", sa.Integer),
)


def upgrade() -> None:
    op.add_column("policy_read_rule", sa.Column("condition", sa.Text))
    op.add_column("policy_read_rule", sa.Column("graphql_version", sa.Integer))

    # Existing rules were written against GraphQL Version 30 and with no condition
    op.execute(policy_read_rule.update().values(condition="", graphql_version=30))

    op.alter_column("policy_read_rule", "condition", nullable=False)
    op.alter_column("policy_read_rule", "graphql_version", nullable=False)


def downgrade() -> None:
    op.drop_column("policy_read_rule", "graphql_version")
    op.drop_column("policy_read_rule", "condition")
