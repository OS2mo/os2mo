# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add active_tils multirange to relation/attr tables

For every relation/attribute table the GraphQL list filters touch, the active
period filter must keep only rows that overlap one of the registration's active
validity periods (gyldighed=Aktiv / publiceret=Publiceret) -- not merely fall in
the filter window independently. Rather than a correlated ``EXISTS`` into the
multi-row ``*_tils_*`` table (whose per-outer-row computed range PostgreSQL
cannot estimate, see #70660), we let Postgres maintain the overlap.

The trick is to split the two-way dependency. ``aktiv_virkning`` (the row's own
``virkning`` intersected with the registration's active-period union) depends on
two things: the row's own ``virkning`` and the registration's ``tils`` rows. So:

* store ``active_tils`` -- the union of the registration's active periods -- on
  each period row. This depends only on ``tils``, so the data flows *one way*
  (``tils`` -> period rows) and the triggers stay trivial, and
* compute the overlap ``tstzmultirange((virkning).timeperiod) * active_tils`` in
  an *expression GiST index* (fused with the ``rel_type`` / ``rel_maal_uuid``
  data filter). It is a pure function of two columns on the same row, so Postgres
  maintains it; the filter becomes ``(... * active_tils) && window``.

``active_tils`` is added NULLable and is deliberately NOT backfilled here:
touching every row in one migration takes too long to run online. A background
job (see ``mora.db.backfill``) fills existing rows in batches, and a follow-up
migration makes it NOT NULL. ``NULL`` therefore means only "not yet backfilled";
a never-active registration gets the empty multirange ``{}``, not ``NULL``.

Maintenance is one-way, so no recursion, dedup or ``pg_trigger_depth()`` guard is
needed:

* a BEFORE INSERT/UPDATE trigger on each period table sets ``active_tils`` from
  the registration's active periods, so it is always non-null at insert -- and
  the backfill's no-op ``UPDATE`` fills existing rows through it,
* an AFTER INSERT/UPDATE/DELETE trigger on the ``tils`` table touches the
  registration's period rows so their BEFORE trigger recomputes ``active_tils``.

The one-way flow means correctness does not depend on insert order (a period row
inserted before its tils is fixed when the tils arrive, and vice versa).

The SQL is written out explicitly per entity in the companion .sql files.
"""

from collections.abc import Sequence

from oio_rest.db.alembic_helpers import apply_sql_from_file

revision: str = "e2a9c47f1b6d"
down_revision: str | Sequence[str] | None = "cfcfa8b6102f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    apply_sql_from_file("e2a9c47f1b6d_add_aktiv_virkning_multirange__upgrade.sql")


def downgrade() -> None:
    apply_sql_from_file("e2a9c47f1b6d_add_aktiv_virkning_multirange__downgrade.sql")
