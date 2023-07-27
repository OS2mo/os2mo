# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add_audit

Revision ID: 82bb9aa9ac4e
Revises: 699bd68b7e73
Create Date: 2023-07-27 16:13:43.158951
"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '82bb9aa9ac4e'
down_revision = '699bd68b7e73'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("client", sa.String, nullable=False),
    )
    op.execute(
        "insert into audit (id, client) values ('42c432e8-9c4a-11e6-9f62-873cf34a735f', 'legacy') on conflict do nothing;"
    )


def downgrade():
    op.drop_table("audit")
