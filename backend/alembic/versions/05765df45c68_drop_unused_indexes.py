# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""drop unused indexes"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "05765df45c68"
down_revision: str | None = "b27228471604"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    apply_sql_from_file("05765df45c68_drop_unused_indexes__upgrade.sql")


def downgrade():
    apply_sql_from_file("05765df45c68_drop_unused_indexes__downgrade.sql")
