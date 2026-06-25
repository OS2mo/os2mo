# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""add aktiv_virkning multirange to relation/attr tables

For every relation/attribute table the GraphQL list filters touch, precompute
``aktiv_virkning``: the row's own ``virkning`` intersected with the union of its
registration's active validity periods (gyldighed=Aktiv / publiceret=Publiceret),
as a ``tstzmultirange``. The active-period filter then becomes a single in-row
multirange overlap ``aktiv_virkning && window`` on the period table itself,
fusable with the data filter (``rel_type`` / ``rel_maal_uuid`` / ...) in one GiST
index, instead of a correlated ``EXISTS`` into the multi-row ``*_tils_*`` table
whose per-outer-row computed range PostgreSQL cannot estimate (see #70660).

Safe on the write path because LoRa inserts ``*_relation`` / ``*_attr_*`` rows
with explicit column lists (a new nullable column is simply ignored), unlike
``*_registrering`` which uses a positional ``ROW(...)::<table>`` cast.

Maintenance: LoRa is append-only (an update writes a new registration version
with fresh rows; existing rows are never mutated), so ``aktiv_virkning`` is
immutable once set. A DEFERRABLE INITIALLY DEFERRED constraint trigger fills it
at COMMIT, by which point all of the registration's ``tils`` rows are present
regardless of the order in which LoRa inserts states/relations/attributes.
``range_agg`` over zero active rows yields NULL, so a row whose registration is
never active gets NULL ``aktiv_virkning`` and matches nothing.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "e2a9c47f1b6d"
down_revision: str | Sequence[str] | None = "cfcfa8b6102f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# (entity prefix, tils table, state column, value meaning "active")
_ENTITIES = [
    ("bruger", "bruger_tils_gyldighed", "gyldighed", "Aktiv"),
    ("facet", "facet_tils_publiceret", "publiceret", "Publiceret"),
    ("itsystem", "itsystem_tils_gyldighed", "gyldighed", "Aktiv"),
    ("klasse", "klasse_tils_publiceret", "publiceret", "Publiceret"),
    ("organisation", "organisation_tils_gyldighed", "gyldighed", "Aktiv"),
    ("organisationenhed", "organisationenhed_tils_gyldighed", "gyldighed", "Aktiv"),
    (
        "organisationfunktion",
        "organisationfunktion_tils_gyldighed",
        "gyldighed",
        "Aktiv",
    ),
]


def _period_tables(entity: str) -> list[tuple[str, bool]]:
    """The entity's period tables, with whether the table carries
    ``rel_type``/``rel_maal_uuid`` (so it gets a composite GiST index)."""
    tables = [
        (f"{entity}_attr_egenskaber", False),
        (f"{entity}_relation", True),
    ]
    if entity == "organisationfunktion":
        tables.append((f"{entity}_attr_udvidelser", False))
    return tables


def upgrade() -> None:
    for entity, tils, state_col, active in _ENTITIES:
        fk = f"{entity}_registrering_id"
        for table, is_relation in _period_tables(entity):
            op.execute(f"ALTER TABLE {table} ADD COLUMN aktiv_virkning tstzmultirange")
            # Backfill: own virkning intersected with the registration's active
            # period union. Registrations with no active period are absent from
            # the subquery, leaving aktiv_virkning NULL (matches nothing).
            op.execute(
                f"UPDATE {table} p "
                f"SET aktiv_virkning = tstzmultirange((p.virkning).timeperiod) * sub.mr "
                f"FROM ("
                f"  SELECT {fk} AS rid, range_agg((virkning).timeperiod) AS mr "
                f"  FROM {tils} WHERE {state_col} = '{active}' GROUP BY {fk}"
                f") sub WHERE p.{fk} = sub.rid"
            )
            op.execute(
                f"CREATE FUNCTION {table}_set_aktiv_virkning() RETURNS trigger AS $$ "
                f"BEGIN "
                f"  UPDATE {table} "
                f"  SET aktiv_virkning = tstzmultirange((virkning).timeperiod) * ("
                f"    SELECT range_agg((t.virkning).timeperiod) FROM {tils} t "
                f"    WHERE t.{fk} = NEW.{fk} AND t.{state_col} = '{active}'"
                f"  ) WHERE id = NEW.id; "
                f"  RETURN NULL; "
                f"END; $$ LANGUAGE plpgsql"
            )
            op.execute(
                f"CREATE CONSTRAINT TRIGGER set_aktiv_virkning "
                f"AFTER INSERT ON {table} DEFERRABLE INITIALLY DEFERRED "
                f"FOR EACH ROW EXECUTE FUNCTION {table}_set_aktiv_virkning()"
            )
            columns = (
                "rel_type, rel_maal_uuid, aktiv_virkning"
                if is_relation
                else "aktiv_virkning"
            )
            op.execute(
                f"CREATE INDEX {table}_aktiv_virkning_idx "
                f"ON {table} USING gist ({columns})"
            )


def downgrade() -> None:
    for entity, _tils, _state_col, _active in _ENTITIES:
        for table, _is_relation in _period_tables(entity):
            op.execute(f"DROP TRIGGER set_aktiv_virkning ON {table}")
            op.execute(f"DROP FUNCTION {table}_set_aktiv_virkning()")
            op.execute(f"DROP INDEX {table}_aktiv_virkning_idx")
            op.execute(f"ALTER TABLE {table} DROP COLUMN aktiv_virkning")
