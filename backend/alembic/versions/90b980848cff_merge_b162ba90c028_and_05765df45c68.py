# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""merge b162ba90c028 and 05765df45c68"""

from collections.abc import Sequence

revision: str = "90b980848cff"
down_revision: str | Sequence[str] | None = ("b162ba90c028", "05765df45c68")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
