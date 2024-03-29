# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""move query_dir to db

Revision ID: 61df86db776f
Revises: b3e16449c312
Create Date: 2024-03-29 21:32:00.000000
"""
import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op


# revision identifiers, used by Alembic.
revision = "61df86db776f"
down_revision = "b3e16449c312"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "idempotency",
        sa.Column("token", sa.Uuid, primary_key=True),
        sa.Column(
            "time",
            sa.DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            index=True,
        ),
        sa.Column("actor", sa.Uuid, nullable=False),
        sa.Column("result", sa.Uuid, nullable=False),
    )


def downgrade():
    op.drop_table("idempotency")
