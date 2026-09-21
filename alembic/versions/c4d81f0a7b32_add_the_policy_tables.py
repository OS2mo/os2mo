# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add the policy tables"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c4d81f0a7b32"
down_revision: str | Sequence[str] | None = "d903192968e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COLLECTION = sa.Enum(
    "Address",
    "Association",
    "Class",
    "Employee",
    "Engagement",
    "Facet",
    "ITSystem",
    "ITUser",
    "KLE",
    "Leave",
    "Manager",
    "Organisation",
    "OrganisationUnit",
    "Owner",
    "RelatedUnit",
    "RoleBinding",
    name="policycollection",
)


def upgrade() -> None:
    op.create_table(
        "policy",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False, index=True),
    )
    op.create_table(
        "policy_read_rule",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("collection", COLLECTION, nullable=False),
        sa.Column("policy_fk", sa.Uuid, sa.ForeignKey("policy.pk"), nullable=False),
    )
    op.create_table(
        "policy_read_rule_field",
        sa.Column(
            "rule_fk",
            sa.Uuid,
            sa.ForeignKey("policy_read_rule.pk"),
            primary_key=True,
        ),
        sa.Column("field", sa.Text, primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("policy_read_rule_field")
    op.drop_table("policy_read_rule")
    op.drop_table("policy")
    COLLECTION.drop(op.get_bind())
