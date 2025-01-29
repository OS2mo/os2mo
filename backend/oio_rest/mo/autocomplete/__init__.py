# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# This code implements autocompletion APIs for employees and org units.
# It assumes that the underlying LoRa database contains the MO extensions
# defined in `mo-01.json`. Thus, it cannot be used with a basic LoRa database
# where the MO extensions have not been installed.
from uuid import UUID

from mora.audit import audit_log
from psycopg import AsyncConnection
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.sql import literal_column
from sqlalchemy.sql import select
from sqlalchemy.sql import text
from sqlalchemy.sql import union

from oio_rest.db.metadata import metadata

# Only search on (partial) UUID if search phrase is longer than this.
# This avoids searching on UUID for short phrases like '1', 'a2', etc.
UUID_SEARCH_MIN_PHRASE_LENGTH = 7


async def get_table(name, connection: AsyncConnection):
    """Return SQLAlchemy `Table` instance of SQL table called `name`"""
    return await connection.run_sync(lambda c: Table(name, metadata, autoload_with=c))


async def find_users_matching(
    session: AsyncSession, phrase: str, class_uuids: list[UUID] | None = None
):
    """Search for users matching `phrase`, returning a list of database rows
    with `uuid` and `name` attributes."""

    # Tables
    connection = await session.connection()
    bruger_reg = await get_table("bruger_registrering", connection)
    bruger_rel = await get_table("bruger_relation", connection)
    bruger_udv = await get_table("bruger_attr_udvidelser", connection)
    orgfunk_reg = await get_table("organisationfunktion_registrering", connection)
    orgfunk_rel = await get_table("organisationfunktion_relation", connection)
    orgfunk_att = await get_table("organisationfunktion_attr_egenskaber", connection)

    # UUID of user
    bruger_uuid = bruger_reg.c.bruger_id.label("uuid")

    # Find hits on UUID
    uuid_hits = (
        select(bruger_uuid)
        .join(bruger_udv, bruger_udv.c.bruger_registrering_id == bruger_reg.c.id)
        .where(
            func.char_length(phrase) > UUID_SEARCH_MIN_PHRASE_LENGTH,
            bruger_reg.c.bruger_id != None,  # noqa: E711
            cast(bruger_reg.c.bruger_id, Text).ilike(phrase),
        )
        .cte()
    )

    # Find hits on name
    name_concated = func.concat(
        bruger_udv.c.fornavn,
        " ",
        bruger_udv.c.efternavn,
        " ",
        bruger_udv.c.kaldenavn_fornavn,
        " ",
        bruger_udv.c.kaldenavn_efternavn,
    )
    name_hits = (
        select(bruger_uuid)
        .join(bruger_udv, bruger_udv.c.bruger_registrering_id == bruger_reg.c.id)
        .where(
            bruger_reg.c.bruger_id != None,  # noqa: E711
            name_concated.ilike(phrase),
        )
        .cte()
    )

    # Find hits on CPR
    cpr_hits = (
        select(bruger_uuid)
        .join(bruger_udv, bruger_udv.c.bruger_registrering_id == bruger_reg.c.id)
        .join(bruger_rel, bruger_rel.c.bruger_registrering_id == bruger_reg.c.id)
        .where(
            bruger_reg.c.bruger_id != None,  # noqa: E711
            bruger_rel.c.rel_maal_urn.ilike(phrase),
        )
        .cte()
    )

    # Find hits on related value (addresses, it systems)
    orgfunk_rel_a = orgfunk_rel.alias()
    orgfunk_rel_b = orgfunk_rel.alias()
    bruger_uuid_rel = orgfunk_rel_a.c.rel_maal_uuid.label("uuid")
    rel_hits = (
        select(bruger_uuid_rel)
        .join(
            orgfunk_rel_b,
            orgfunk_rel_a.c.organisationfunktion_registrering_id
            == orgfunk_rel_b.c.organisationfunktion_registrering_id,
        )
        .join(
            orgfunk_reg,
            orgfunk_rel_a.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .join(
            orgfunk_att,
            orgfunk_att.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .where(
            orgfunk_rel_a.c.rel_maal_uuid != None,  # noqa: E711
            orgfunk_rel_a.c.rel_type == "tilknyttedebrugere",
            orgfunk_rel_b.c.rel_type.in_(["adresser", "tilknyttedeitsystemer"]),
            orgfunk_att.c.brugervendtnoegle.ilike(phrase),
        )
        .cte()
    )

    # Union of hits on UUID, name, CPR and related values
    selects = [select(cte.c.uuid) for cte in (uuid_hits, name_hits, cpr_hits, rel_hits)]
    all_hits = union(*selects).cte()

    # Decorate results with user's full name and selected related values
    orgfunk_rel_other = orgfunk_rel.alias()

    current_user_name = func.jsonb_agg(
        func.concat(bruger_udv.c.fornavn, " ", bruger_udv.c.efternavn),
        type_=postgresql.JSONB,
    ).filter(text("(bruger_attr_udvidelser.virkning).timeperiod @> now()"))[0]

    attrs = func.jsonb_agg(
        func.distinct(
            func.jsonb_build_array(
                orgfunk_rel_other.c.rel_maal_uuid,
                orgfunk_att.c.brugervendtnoegle,
            ),
        ),
    )
    if class_uuids:
        attrs = attrs.filter(
            orgfunk_rel_other.c.rel_maal_uuid.in_(map(str, class_uuids))
        )

    decorated_hits = (
        select(bruger_uuid, current_user_name.label("name"), attrs.label("attrs"))
        .join(bruger_udv, bruger_udv.c.bruger_registrering_id == bruger_reg.c.id)
        .outerjoin(orgfunk_rel, bruger_uuid == orgfunk_rel.c.rel_maal_uuid)
        .outerjoin(
            orgfunk_reg,
            orgfunk_rel.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .outerjoin(
            orgfunk_att,
            orgfunk_att.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .outerjoin(
            orgfunk_rel_other,
            (orgfunk_rel.c.id != orgfunk_rel_other.c.id)
            & (
                orgfunk_rel.c.organisationfunktion_registrering_id
                == orgfunk_rel_other.c.organisationfunktion_registrering_id
            )
            & (
                orgfunk_rel_other.c.rel_type.in_(
                    ["organisatoriskfunktionstype", "tilknyttedeitsystemer"]
                )
            ),
        )
        .where(bruger_uuid == all_hits.c.uuid)
        .group_by(bruger_uuid)
    )

    query = decorated_hits
    limit = 1000
    result = await session.execute(query.limit(limit))
    rows = result.mappings().fetchall()
    uuids = [x["uuid"] for x in rows]
    # TODO: Log org-funk lookups
    # TODO: Log class lookups
    audit_log(
        session,
        "find_users_matching",
        "Bruger",
        {"phrase": phrase, "class_uuids": class_uuids},
        uuids,
    )
    return rows


async def find_org_units_matching(
    session: AsyncSession, phrase: str, class_uuids: list[UUID] | None = None
):
    """Search for organisation units matching `phrase`, returning a list of
    database rows with `uuid` and `name` attributes."""

    # Tables
    connection = await session.connection()
    enhed_reg = await get_table("organisationenhed_registrering", connection)
    enhed_att = await get_table("organisationenhed_attr_egenskaber", connection)
    orgfunk_reg = await get_table("organisationfunktion_registrering", connection)
    orgfunk_rel = await get_table("organisationfunktion_relation", connection)
    orgfunk_att = await get_table("organisationfunktion_attr_egenskaber", connection)

    # UUID of org unit
    enhed_uuid = enhed_reg.c.organisationenhed_id.label("uuid")

    # Find hits on UUID
    uuid_hits = (
        select(enhed_uuid)
        .join(
            enhed_att,
            enhed_att.c.organisationenhed_registrering_id == enhed_reg.c.id,
        )
        .where(
            func.char_length(phrase) > UUID_SEARCH_MIN_PHRASE_LENGTH,
            enhed_reg.c.organisationenhed_id != None,  # noqa: E711
            cast(enhed_reg.c.organisationenhed_id, Text).ilike(phrase),
        )
        .cte()
    )

    # Find hits on name
    name_hits = (
        select(enhed_uuid)
        .join(
            enhed_att,
            enhed_att.c.organisationenhed_registrering_id == enhed_reg.c.id,
        )
        .where(
            enhed_reg.c.organisationenhed_id != None,  # noqa: E711
            (
                enhed_att.c.enhedsnavn.ilike(phrase)
                | enhed_att.c.brugervendtnoegle.ilike(phrase)
            ),
        )
        .cte()
    )

    # Find hits on related value (addresses, it systems)
    orgfunk_rel_a = orgfunk_rel.alias()
    orgfunk_rel_b = orgfunk_rel.alias()
    enhed_uuid_rel = orgfunk_rel_a.c.rel_maal_uuid.label("uuid")
    rel_hits = (
        select(enhed_uuid_rel)
        .outerjoin(
            enhed_reg,
            enhed_reg.c.organisationenhed_id == orgfunk_rel_a.c.rel_maal_uuid,
        )
        .outerjoin(
            enhed_att,
            enhed_att.c.organisationenhed_registrering_id == enhed_reg.c.id,
        )
        .outerjoin(
            orgfunk_rel_b,
            orgfunk_rel_a.c.organisationfunktion_registrering_id
            == orgfunk_rel_b.c.organisationfunktion_registrering_id,
        )
        .outerjoin(
            orgfunk_reg,
            orgfunk_rel_a.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .outerjoin(
            orgfunk_att,
            orgfunk_att.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .where(
            orgfunk_rel_a.c.rel_maal_uuid != None,  # noqa: E711
            orgfunk_rel_a.c.rel_type.in_(["tilknyttedeenheder"]),
            orgfunk_rel_b.c.rel_type.in_(["adresser", "tilknyttedeitsystemer"]),
            orgfunk_att.c.brugervendtnoegle.ilike(phrase),
        )
        .cte()
    )

    # Union of hits on UUID, name, and related values
    selects = [select(cte.c.uuid) for cte in (uuid_hits, name_hits, rel_hits)]
    all_hits = union(*selects).cte()

    # Decorate results with unit's full name and selected related values
    current_org_units_only = text(
        "(organisationenhed_attr_egenskaber.virkning).timeperiod @> now()"
    )
    current_org_unit_name = func.jsonb_agg(
        enhed_att.c.enhedsnavn, type_=postgresql.JSONB
    ).filter(current_org_units_only)[0]

    orgfunk_rel_other = orgfunk_rel.alias()

    attrs = func.jsonb_agg(
        func.distinct(
            func.jsonb_build_array(
                orgfunk_rel_other.c.rel_maal_uuid,
                orgfunk_att.c.brugervendtnoegle,
            )
        ),
    )
    if class_uuids:
        attrs = attrs.filter(
            orgfunk_rel_other.c.rel_maal_uuid.in_(map(str, class_uuids))
        )

    decorated_hits = (
        select(
            enhed_uuid,
            current_org_unit_name.label("name"),
            (await _org_unit_path(session, all_hits, enhed_uuid)).label("path"),
            attrs.label("attrs"),
        )
        .join(
            enhed_att,
            enhed_att.c.organisationenhed_registrering_id == enhed_reg.c.id,
        )
        .join(orgfunk_rel, enhed_uuid == orgfunk_rel.c.rel_maal_uuid)
        .join(
            orgfunk_reg,
            orgfunk_rel.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .join(
            orgfunk_att,
            orgfunk_att.c.organisationfunktion_registrering_id == orgfunk_reg.c.id,
        )
        .join(
            orgfunk_rel_other,
            (orgfunk_rel.c.id != orgfunk_rel_other.c.id)
            & (
                orgfunk_rel.c.organisationfunktion_registrering_id
                == orgfunk_rel_other.c.organisationfunktion_registrering_id
            )
            & (
                orgfunk_rel_other.c.rel_type.in_(
                    ["organisatoriskfunktionstype", "tilknyttedeitsystemer"]
                )
            ),
        )
        .where(enhed_uuid == all_hits.c.uuid)
        .group_by(enhed_uuid)
    )

    query = decorated_hits
    limit = 1000
    result = await session.execute(query.limit(limit))
    rows = result.mappings().fetchall()
    uuids = [x["uuid"] for x in rows]
    # TODO: Log org-funk lookups
    # TODO: Log class lookups
    audit_log(
        session,
        "find_org_units_matching",
        "OrganisationEnhed",
        {"phrase": phrase, "class_uuids": class_uuids},
        uuids,
    )
    return rows


async def _org_unit_path(session, all_hits, enhed_uuid):
    # Construct a scalar subselect which will return the path for each found
    # org unit in `all_hits`.
    connection = await session.connection()
    org = await get_table("organisation", connection)
    enhed_reg = await get_table("organisationenhed_registrering", connection)
    enhed_rel = await get_table("organisationenhed_relation", connection)
    enhed_att = await get_table("organisationenhed_attr_egenskaber", connection)

    # Base CTE:
    # Initialize the recursion with the UUID of the found org unit, as well as
    # an empty array of strings, which will eventually hold the org unit path.
    nodes_cte = select(
        # "Base" org unit UUID (same for all rows in result)
        all_hits.c.uuid.label("base_id"),
        # Current org unit UUID (different for each row in result)
        all_hits.c.uuid.label("id"),
        # Empty array of strings (will be populated the in accumulative CTE
        # below.)
        literal_column("array[]::text[]").label("p"),
    ).cte(recursive=True)

    # Accumulative CTE:
    # Follow the parent ("overordnet") relation of each unit up to its root.
    # Prepend each org unit name to the array 'p'.
    nodes_recursive = nodes_cte.alias()
    nodes_cte = nodes_cte.union(
        select(
            # Keep the UUID of the base org unit (same for all rows in CTE)
            nodes_recursive.columns.base_id,
            # Record the UUID of the current parent org unit
            enhed_rel.c.rel_maal_uuid,
            # Prepend the name of the current org unit onto path 'p'
            func.array_prepend(enhed_att.c.enhedsnavn, nodes_recursive.columns.p),
        )
        .join(
            enhed_reg,
            enhed_reg.c.id == enhed_rel.c.organisationenhed_registrering_id,
        )
        .join(
            enhed_att,
            enhed_reg.c.id == enhed_att.c.organisationenhed_registrering_id,
        )
        .join(
            nodes_recursive,
            nodes_recursive.columns.id == enhed_reg.c.organisationenhed_id,
        )
        .where(
            enhed_rel.c.rel_type == "overordnet",
            text("(organisationenhed_relation.virkning).timeperiod @> now()"),
            text("(organisationenhed_attr_egenskaber.virkning).timeperiod @> now()"),
        )
    )

    return (
        # Take first *complete* path (only 1 is expected)
        select(func.json_agg(nodes_cte.columns.p, type_=postgresql.JSONB)[0]).where(
            # A complete path must start at the current org unit UUID
            nodes_cte.columns.base_id == enhed_uuid,
            # A complete path must contain the root org unit UUID
            nodes_cte.columns.id.in_(select(org.c.id)),
        )
    )
