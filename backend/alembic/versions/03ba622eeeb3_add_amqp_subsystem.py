# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add amqp_subsystem"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "03ba622eeeb3"
down_revision: str | None = "90b980848cff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.create_table(
        "amqp_subsystem",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("last_run", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        "insert into amqp_subsystem (id, last_run) values (1, now()) on conflict do nothing;"
    )


def downgrade():
    op.drop_table("amqp_subsystem")
