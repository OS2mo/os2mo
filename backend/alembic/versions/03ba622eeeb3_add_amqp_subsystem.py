# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add amqp_subsystem

Revision ID: 03ba622eeeb3
Revises: 90b980848cff
Create Date: 2023-03-09 10:35:01.223191
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "03ba622eeeb3"
down_revision = "90b980848cff"
branch_labels = None
depends_on = None


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
