# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

"""Change exception to notice to keep transaction intact

Revision ID: aabbadb79841
Revises: b3e16449c312
Create Date: 2024-05-23 13:53:19.221030
"""

from typing import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file


# revision identifiers, used by Alembic.
revision: str = "aabbadb79841"
down_revision: str | None = "b3e16449c312"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("aabbadb79841_change_exception_to_notice.sql")


def downgrade() -> None:
    pass
