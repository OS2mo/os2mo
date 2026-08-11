# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Policy rule condition"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e8f9a0b1c2d3"
down_revision: str | Sequence[str] | None = "c6d7e8f9a0b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "policy_rule",
        # Optional CEL condition that must hold for the rule to apply
        sa.Column(
            "condition",
            sa.Text,
            nullable=False,
            server_default="",
        ),
    )
    op.drop_constraint("uq_policy_rule", "policy_rule", type_="unique")
    op.create_unique_constraint(
        "uq_policy_rule",
        "policy_rule",
        ["policy_fk", "type", "field", "condition"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_policy_rule", "policy_rule", type_="unique")
    op.create_unique_constraint(
        "uq_policy_rule",
        "policy_rule",
        ["policy_fk", "type", "field"],
    )
    op.drop_column("policy_rule", "condition")
