# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add file_tokens

Revision ID: 786610e88e1c
Revises: 69ca41b4011e
Create Date: 2023-06-27 15:59:35.949549
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "699bd68b7e73"
down_revision = "03ba622eeeb3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "file_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, default=func.now()
        ),
        sa.Column("secret", sa.String(255), nullable=False),
    )


def downgrade():
    op.drop_table("file_tokens")
