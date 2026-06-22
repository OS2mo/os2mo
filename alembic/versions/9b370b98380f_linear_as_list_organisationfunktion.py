# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""linear as_list_organisationfunktion"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "9b370b98380f"
down_revision: str | Sequence[str] | None = "aeb818ae64be"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("9b370b98380f_linear_as_list_organisationfunktion__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file(
        "9b370b98380f_linear_as_list_organisationfunktion__downgrade.sql"
    )
