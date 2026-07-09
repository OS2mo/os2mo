# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""make active_tils NOT NULL

By this point the background job (see ``mora.db.backfill``) has populated
``active_tils`` on every existing row (``NULL`` meant "not yet backfilled"; see
``e2a9c47f1b6d``), so the column can be made NOT NULL.

Unlike a deferred trigger, the BEFORE INSERT/UPDATE trigger sets ``active_tils``
synchronously as the row is written, so new rows are already non-null at INSERT
and no DEFAULT is needed. ``SET NOT NULL`` scans the table once to verify no
NULLs remain -- a read-only verification, cheap next to the per-row work the
backfill already did out of band.

The SQL is written out explicitly per table in the companion .sql files.
"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "b4e8d2f16a3c"
down_revision: str | Sequence[str] | None = "e2a9c47f1b6d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("b4e8d2f16a3c_aktiv_virkning_not_null__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("b4e8d2f16a3c_aktiv_virkning_not_null__downgrade.sql")
