# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""remove integrationsdata"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "b162ba90c028"
down_revision: str | Sequence[str] | None = "b27228471604"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("b162ba90c028_remove_integrationsdata__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("b162ba90c028_remove_integrationsdata__downgrade.sql")
