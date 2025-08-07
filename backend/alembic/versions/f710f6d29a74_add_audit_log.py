# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Add audit_log."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

revision: str = "f710f6d29a74"
down_revision: str | None = "9525559842d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.create_table(
        "audit_log_operation",
        sa.Column(
            "id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "time",
            sa.DateTime(timezone=True),
            nullable=False,
            default=func.now(),
            index=True,
        ),
        sa.Column("actor", sa.Uuid, nullable=False, index=True),
        sa.Column("model", sa.String(255), nullable=False, index=True),
        sa.Column("operation", sa.String(255), nullable=False),
        sa.Column("arguments", sa.JSON, nullable=False),
    )
    op.create_table(
        "audit_log_read",
        sa.Column(
            "id",
            sa.Uuid,
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("operation_id", sa.Uuid, sa.ForeignKey("audit_log_operation.id")),
        sa.Column("uuid", sa.Uuid, nullable=False, index=True),
    )


def downgrade():
    op.drop_table("audit_log_operation")
    op.drop_table("audit_log_read")
