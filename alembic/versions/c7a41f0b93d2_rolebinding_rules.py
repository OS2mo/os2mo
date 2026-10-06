# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c7a41f0b93d2"
down_revision: str | Sequence[str] | None = "5e0c7a4f2d19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "rolebinding_rule",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_table(
        "rolebinding_rule_revision",
        sa.Column("pk", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column(
            "rule_fk",
            sa.Uuid,
            sa.ForeignKey("rolebinding_rule.pk"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("actor", sa.Uuid, nullable=False),
        sa.Column("deleted", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("user_key", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Uuid, nullable=False),
        sa.Column("expression", sa.String, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("rolebinding_rule_revision")
    op.drop_table("rolebinding_rule")
