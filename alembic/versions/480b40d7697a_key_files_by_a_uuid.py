# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Key files by a uuid"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "480b40d7697a"
down_revision: str | Sequence[str] | None = "616363657373"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "file",
        sa.Column(
            "uuid",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text("uuid_generate_v4()"),
        ),
    )
    # Drop the existing primary key and make uuid the primary key
    op.drop_column("file", "id")
    op.create_primary_key("file_pkey", "file", ["uuid"])


def downgrade() -> None:
    op.drop_column("file", "uuid")
    op.execute("ALTER TABLE file ADD COLUMN id serial PRIMARY KEY")
