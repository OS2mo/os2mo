# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Move the role of a policy into a selector"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "5e0c7a4f2d19"
down_revision: str | Sequence[str] | None = "b5332b0a9276"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SELECTOR_KIND = sa.Enum("role", name="policyselectorkind")

policy = sa.table(
    "policy",
    sa.column("pk", sa.Uuid),
    sa.column("role", sa.Text),
)
policy_selector = sa.table(
    "policy_selector",
    sa.column("kind", SELECTOR_KIND),
    sa.column("value", sa.Text),
    sa.column("policy_fk", sa.Uuid),
)


def upgrade() -> None:
    op.create_table(
        "policy_selector",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("kind", SELECTOR_KIND, nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column(
            "policy_fk",
            sa.Uuid,
            sa.ForeignKey("policy.pk", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("policy_fk", "kind", "value", name="uq_policy_selector"),
    )
    op.execute(
        policy_selector.insert().from_select(
            ["kind", "value", "policy_fk"],
            sa.select(sa.cast("role", SELECTOR_KIND), policy.c.role, policy.c.pk),
        )
    )
    op.drop_column("policy", "role")


def downgrade() -> None:
    op.add_column("policy", sa.Column("role", sa.Text))
    # A policy holds a single role, so it keeps the first it is selected by,
    # and one selected by none is left to nobody
    op.execute(
        policy.update().values(
            role=sa.func.coalesce(
                sa.select(sa.func.min(policy_selector.c.value))
                .where(
                    policy_selector.c.policy_fk == policy.c.pk,
                    policy_selector.c.kind == "role",
                )
                .scalar_subquery(),
                "__unknown__",
            )
        )
    )
    op.alter_column("policy", "role", nullable=False)
    op.create_index("ix_policy_role", "policy", ["role"])
    op.drop_table("policy_selector")
    SELECTOR_KIND.drop(op.get_bind())
