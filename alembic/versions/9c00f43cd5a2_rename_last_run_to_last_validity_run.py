# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""rename last_run to last_validity_run"""

from collections.abc import Sequence

from alembic import op

revision: str = "9c00f43cd5a2"
down_revision: str | Sequence[str] | None = "cfcfa8b6102f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "alter table amqp_subsystem rename column last_run to last_validity_run;"
    )


def downgrade() -> None:
    op.execute(
        "alter table amqp_subsystem rename column last_validity_run to last_run;"
    )
