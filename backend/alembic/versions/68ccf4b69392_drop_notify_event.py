# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""drop notify_event()"""

from collections.abc import Sequence

from alembic import op

revision: str = "68ccf4b69392"
down_revision: str | None = "b3e16449c312"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("drop function notify_event cascade;")


def downgrade() -> None:
    # notify_event() has not been used for years. No need for a downgrade.
    pass
