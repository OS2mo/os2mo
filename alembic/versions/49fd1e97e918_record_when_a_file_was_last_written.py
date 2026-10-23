# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Record when a file was last written"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "49fd1e97e918"
down_revision: str | Sequence[str] | None = "a495fe4cf82a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

file = sa.table(
    "file",
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    op.add_column("file", sa.Column("updated_at", sa.DateTime(timezone=True)))
    # When existing files were last overwritten is unknown, so they get the
    # time they were created
    op.execute(file.update().values(updated_at=file.c.created_at))
    op.alter_column("file", "updated_at", nullable=False)


def downgrade() -> None:
    op.drop_column("file", "updated_at")
