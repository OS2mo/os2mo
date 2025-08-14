# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""move query_dir to db"""

import os
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

revision: str = "b3e16449c312"
down_revision: str | Sequence[str] | None = "f710f6d29a74"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    table = op.create_table(
        "file",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, default=func.now()
        ),
        sa.Column("actor", sa.Uuid, nullable=False),
        sa.Column("store", sa.String(255), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("content", sa.LargeBinary, nullable=False),
        sa.UniqueConstraint("store", "name", name="uix_store_name"),
    )

    files = []
    # Currently, there only exists "queries", so no insights folder is
    # migrated. All known MO installations use the same directory.
    for filename in os.listdir("/queries"):
        try:
            with open("/queries/" + filename, "rb") as f:
                content = f.read()
                files.append(
                    {
                        "actor": "42c432e8-9c4a-11e6-9f62-873cf34a735f",  # magic legacy UUID
                        "store": "EXPORTS",
                        "name": filename,
                        "content": content,
                    }
                )
        except IsADirectoryError:
            pass

    op.bulk_insert(table, files)


def downgrade() -> None:
    op.drop_table("file")
