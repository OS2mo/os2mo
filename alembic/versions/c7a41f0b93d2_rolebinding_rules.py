# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c7a41f0b93d2"
down_revision: str | Sequence[str] | None = "6e616d657370"
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
        ),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "actor",
            sa.Uuid,
            sa.ForeignKey("actor.actor", name="rolebinding_rule_revision_actor_fkey"),
            nullable=False,
        ),
        sa.Column("deleted", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column(
            "role",
            sa.Uuid,
            sa.ForeignKey("klasse.id", name="rolebinding_rule_revision_role_fkey"),
            nullable=False,
        ),
        sa.Column("expression", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False),
        sa.UniqueConstraint(
            "rule_fk", "version", name="rolebinding_rule_revision_version_key"
        ),
    )


def downgrade() -> None:
    op.drop_table("rolebinding_rule_revision")
    op.drop_table("rolebinding_rule")
