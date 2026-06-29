# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add policy_actor table"""

# TODO: Before release, merge this migration into the prior policy migrations
# (the policy table and the policyadmin bootstrap) so policies ship as a single
# migration rather than this incremental dev history.

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4bf31456c509"
down_revision: str | Sequence[str] | None = "426b7b762dae"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Magic UUID; keep in sync with mora.db.policies.POLICYADMIN_UUID.
POLICYADMIN_UUID = "ded1ca7e-9bac-5eed-706f-6c61646d696e"


def upgrade() -> None:
    op.create_table(
        "policy_actor",
        sa.Column(
            "pk",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        # Actor attribute to match on: "uuid", "username" or "role".
        sa.Column("kind", sa.String(255), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column(
            "policy_fk",
            sa.Uuid,
            sa.ForeignKey("policy.id"),
            nullable=False,
        ),
        # Makes `policy_actor_declare` idempotent.
        sa.UniqueConstraint(
            "policy_fk", "kind", "value", name="uq_policy_actor"
        ),
    )

    # The bootstrap Policy Administrator policy is hard-bound to the "admin"
    # role. This binding (like the policy itself) is protected from modification.
    op.execute(
        f"""
        INSERT INTO policy_actor (kind, value, policy_fk)
        VALUES ('role', 'admin', '{POLICYADMIN_UUID}')
        """
    )


def downgrade() -> None:
    op.drop_table("policy_actor")
