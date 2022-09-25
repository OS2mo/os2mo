# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""Added Idempotency Table

Revision ID: 76a1d372255e
Revises: 90b980848cff
Create Date: 2022-09-25 00:21:55.750340
"""
from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import UniqueConstraint
from sqlalchemy_utils.types.uuid import UUIDType

from alembic.op import create_table
from alembic.op import drop_table

# revision identifiers, used by Alembic.
revision = "76a1d372255e"
down_revision = "90b980848cff"
branch_labels = None
depends_on = None


table_name = "idempotency_token"


def upgrade():
    create_table(
        table_name,
        Column("id", UUIDType(binary=False), nullable=False),
        Column("token", String(length=256), nullable=False),
        Column("expiration", TIMESTAMP(timezone=True), nullable=False),
        PrimaryKeyConstraint("id"),
        UniqueConstraint("token"),
    )


def downgrade():
    drop_table(table_name)
