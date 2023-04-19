# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from contextlib import suppress
from datetime import date
from datetime import datetime
from datetime import time
from itertools import starmap
from uuid import UUID

from sqlalchemy import cast
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql import literal_column
from sqlalchemy.sql import select
from sqlalchemy.sql import text
from sqlalchemy.sql import union

from mora import common
from mora import util
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.lora import AutocompleteScope


async def get_results(
    entity: str, class_uuids: list[UUID], query: str
) -> dict[str, list]:
    """Run an autocomplete search query.

    Args:
        entity:
            The entity type to autocomplete.
            One of 'bruger' and 'organisationsenhed'.
        class_uuids:
            List of class UUIDs whose title and value will be displayed for match.
        query:
            The search query string.

    Returns:
        A dictionary with key 'items' and a value that are the matches.
    """
    if not query:
        return {"items": []}

    connector = common.get_connector()
    # Build map of {uuid: class data} so that we can look up each class title later.
    class_uuids = class_uuids or []
    loaded_classes = await gather(*map(connector.klasse.get, class_uuids))
    class_map = dict(zip(class_uuids, loaded_classes))

    # Fetch autocomplete results from LoRa
    scope = AutocompleteScope(connector, entity)
    results = await scope.fetch(
        phrase=util.query_to_search_phrase(query),
        class_uuids=class_uuids,
    )

    def convert_attrs(class_uuid, value):
        title = None
        with suppress((KeyError, TypeError)):
            class_data = class_map[UUID(class_uuid)]
            title = class_data["attributter"]["klasseegenskaber"][0]["titel"]
        return {
            "uuid": class_uuid,
            "value": value,
            "title": title,
        }

    # Add class title to each attr of each result
    for result in results["items"]:
        attrs = result.get("attrs")
        if attrs is None:
            continue
        result["attrs"] = list(starmap(convert_attrs, attrs))

    return results


async def search_orgunits(sessionmaker, search_phrase: str, at: date | None = None):
    sql_at_datetime = _get_at_date_sql(at)

    async with sessionmaker() as session:
        cte_uuid_hits = _get_cte_orgunit_uuid_hits(search_phrase, sql_at_datetime)
        cte_name_hits = _get_cte_orgunit_name_hits(search_phrase, sql_at_datetime)
        cte_addr_hits = _get_cte_orgunit_addr_hits(search_phrase, sql_at_datetime)

        cte_itsystems_hits = _get_cte_orgunit_itsystem_hits(
            search_phrase, sql_at_datetime
        )

        # UNION all the queries
        selects = [
            select(cte.c.uuid)
            for cte in (
                cte_uuid_hits,
                cte_name_hits,
                cte_addr_hits,
                # hits_orgunit_itsystems,
            )
        ]
        all_hits = union(*selects).cte()

        # FINAL query
        query_final = (
            select(
                OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"),
            )
            .where(
                OrganisationEnhedRegistrering.organisationenhed_id == all_hits.c.uuid
            )
            .group_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )

        # Execute & parse results
        r = await session.execute(query_final)
        return _read_gql_response(r)


def _read_gql_response(response):
    result = []
    while True:
        chunk = response.fetchmany(1000)
        if not chunk:
            break

        for row in chunk:
            result.append(row)

    return result


async def _read_session_results(chunk_results):
    while True:
        chunk = chunk_results.fetchmany(1000)
        if not chunk:
            break

        for row in chunk:
            yield row


def _get_at_date_sql(at: date | None = None):
    sql_at_datetime = "now()"
    if at is not None:
        sql_at_datetime = (
            f"to_timestamp('{datetime.combine(at, time.min).isoformat()}', "
            "'YYYY-MM-DD HH24:MI:SS')"
        )

    return sql_at_datetime


def _get_cte_orgunit_uuid_hits(search_phrase: str, sql_at_datetime: str):
    return (
        select(OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"))
        .join(
            OrganisationEnhedAttrEgenskaber,
            OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
            == OrganisationEnhedRegistrering.id,
        )
        .where(
            func.char_length(search_phrase) > 7,
            OrganisationEnhedRegistrering.organisationenhed_id != None,  # noqa: E711
            cast(OrganisationEnhedRegistrering.organisationenhed_id, Text).ilike(
                search_phrase
            ),
            text(
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {sql_at_datetime}"
            ),
        )
        .cte()
    )


def _get_cte_orgunit_name_hits(search_phrase: str, sql_at_datetime: str):
    return (
        select(OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"))
        .join(
            OrganisationEnhedAttrEgenskaber,
            OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
            == OrganisationEnhedRegistrering.id,
        )
        .where(
            OrganisationEnhedRegistrering.organisationenhed_id != None,  # noqa: E711
            (
                OrganisationEnhedAttrEgenskaber.enhedsnavn.ilike(search_phrase)
                | OrganisationEnhedAttrEgenskaber.brugervendtnoegle.ilike(search_phrase)
            ),
            text(
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {sql_at_datetime}"
            ),
        )
        .cte()
    )


def _get_cte_orgunit_addr_hits(search_phrase: str, sql_at_datetime: str):
    # primary lookup table
    orgfunc_tbl_rels_a = aliased(OrganisationFunktionRelation)
    orgunit_uuid_col = orgfunc_tbl_rels_a.rel_maal_uuid.label("uuid")

    # Secondary lookup table (cause addrs values are located in another row for same registration)
    orgfunc_tbl_rels_b = aliased(OrganisationFunktionRelation)

    return (
        select(orgunit_uuid_col)
        .outerjoin(
            orgfunc_tbl_rels_b,
            orgfunc_tbl_rels_b.organisationfunktion_registrering_id
            == orgfunc_tbl_rels_a.organisationfunktion_registrering_id,
        )
        .where(
            orgfunc_tbl_rels_a.rel_maal_uuid != None,  # noqa: E711
            cast(orgfunc_tbl_rels_a.rel_type, String)
            == OrganisationFunktionRelationKode.tilknyttedeenheder,
            text(
                f"(organisationfunktion_relation_1.virkning).timeperiod @> {sql_at_datetime}"
            ),
            orgfunc_tbl_rels_b.rel_maal_urn != None,  # noqa: E711
            cast(orgfunc_tbl_rels_b.rel_type, String)
            == OrganisationFunktionRelationKode.adresser,
            orgfunc_tbl_rels_b.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


def _get_cte_orgunit_itsystem_hits(search_phrase: str, sql_at_datetime: str):
    pass


# ----------------------------------------------------------------------------------------------------------------


async def search_orgunits_old(sessionmaker, search_phrase: str, at: date | None = None):
    if not search_phrase:
        return {"items": []}

    # Handle timemachine-/at-date
    at_datetime_str_sql = "now()"
    if at is not None:
        at_datetime_str_sql = (
            f"to_timestamp('{datetime.combine(at, time.min).isoformat()}', "
            "'YYYY-MM-DD HH24:MI:SS')"
        )

    async with sessionmaker() as session:
        r = await session.scalar(select(OrganisationEnhedRegistrering).limit(1000))

        r2 = await session.execute(
            select(OrganisationEnhedRegistrering.organisationenhed_id)
            .join(
                OrganisationEnhedAttrEgenskaber,
                OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
                == OrganisationEnhedRegistrering.id,
            )
            .where(
                func.char_length(search_phrase) > 7,
                OrganisationEnhedRegistrering.organisationenhed_id
                != None,  # noqa: E711
                cast(OrganisationEnhedRegistrering.organisationenhed_id, Text).ilike(
                    search_phrase
                ),
                text(
                    f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_datetime_str_sql}"
                ),
            )
        )

        while True:
            chunk = r2.fetchmany(1000)
            if not chunk:
                break

            for row in chunk:
                # process the row
                print(row)

        tap = "test"

    # ---------------------------------------------------------------------------------------------------------------

    db_engine = get_engine()

    # Find orgunit UUID hits
    orgunit_tbl_regs = get_table("organisationenhed_registrering", db_engine)
    orgunit_tbl_attrs = get_table("organisationenhed_attr_egenskaber", db_engine)
    orgfunc_tbl_rels = get_table("organisationfunktion_relation", db_engine)
    orgfunc_tbl_attrs = get_table("organisationfunktion_attr_egenskaber", db_engine)

    orgunit_reg_col_uuid = orgunit_tbl_regs.c.organisationenhed_id.label("uuid")

    # Create CommonTableExpressions (CTE) / search-queries,
    # for all the parts we want to search through
    hits_orgunit_uuid = _orgunit_uuid_hits_query(
        orgunit_tbl_regs, orgunit_tbl_attrs, search_phrase, at_datetime_str_sql
    )
    hits_orgunit_name = _orgunit_name_hits_query(
        orgunit_tbl_regs,
        orgunit_tbl_attrs,
        orgunit_reg_col_uuid,
        search_phrase,
        at_datetime_str_sql,
    )
    hits_orgunit_addrs = _orgunit_rel_addr_hits_query(
        orgfunc_tbl_rels, search_phrase, at_datetime_str_sql
    )
    hits_orgunit_itsystems = _orgunit_rel_itsystems_hits_query(
        orgfunc_tbl_rels, orgfunc_tbl_attrs, search_phrase, at_datetime_str_sql
    )

    # UNION sub queries
    selects = [
        select(cte.c.uuid)
        for cte in (
            hits_orgunit_uuid,
            hits_orgunit_name,
            hits_orgunit_addrs,
            hits_orgunit_itsystems,
        )
    ]
    all_hits = union(*selects).cte()

    # Create final query and run it
    q = (
        select(
            orgunit_reg_col_uuid,
            _org_unit_path(
                db_engine, all_hits, orgunit_reg_col_uuid, at_datetime_str_sql
            ).label("path"),
        )
        .where(orgunit_reg_col_uuid == all_hits.c.uuid)
        .group_by(orgunit_reg_col_uuid)
    )

    result = await session.execute(q.limit(1000))
    return result.mappings().fetchall()

    # async with sessionmaker() as session:
    #     result = await session.execute(q.limit(1000))
    #     return result.mappings().fetchall()
    # return execute_query(q, db_engine)


# PRIVATE methods


def _orgunit_uuid_hits_query(
    orgunit_tbl_regs, orgunit_tbl_attrs, search_phrase: str, at_datetime_str_sql: str
):
    # TODO: Do we use the JOIN on "orgunit_tbl_attrs" for anything? looks we can just remove it
    return (
        select(orgunit_tbl_regs.c.organisationenhed_id.label("uuid"))
        .join(
            orgunit_tbl_attrs,
            orgunit_tbl_attrs.c.organisationenhed_registrering_id
            == orgunit_tbl_regs.c.id,
        )
        .where(
            func.char_length(search_phrase) > 7,
            orgunit_tbl_regs.c.organisationenhed_id != None,  # noqa: E711
            cast(orgunit_tbl_regs.c.organisationenhed_id, Text).ilike(search_phrase),
            text(
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_datetime_str_sql}"
            ),
        )
        .cte()
    )


def _orgunit_name_hits_query(
    orgunit_tbl_regs,
    orgunit_tbl_attrs,
    orgunit_reg_col_uuid,
    search_phrase: str,
    at_datetime_str_sql: str,
):
    return (
        select(orgunit_reg_col_uuid)
        .join(
            orgunit_tbl_attrs,
            orgunit_tbl_attrs.c.organisationenhed_registrering_id
            == orgunit_tbl_regs.c.id,
        )
        .where(
            orgunit_tbl_regs.c.organisationenhed_id != None,  # noqa: E711
            (
                orgunit_tbl_attrs.c.enhedsnavn.ilike(search_phrase)
                | orgunit_tbl_attrs.c.brugervendtnoegle.ilike(search_phrase)
            ),
            text(
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_datetime_str_sql}"
            ),
        )
        .cte()
    )


def _orgunit_rel_addr_hits_query(
    orgfunc_tbl_rels, search_phrase: str, at_datetime_str_sql: str
):
    # primary lookup table
    orgfunc_tbl_rels_a = orgfunc_tbl_rels.alias()
    orgunit_uuid_col = orgfunc_tbl_rels_a.c.rel_maal_uuid.label("uuid")

    # Secondary lookup table (cause addrs values are located in another row for same registration)
    orgfunc_tbl_rels_b = orgfunc_tbl_rels.alias()

    return (
        select(orgunit_uuid_col)
        .outerjoin(
            orgfunc_tbl_rels_b,
            orgfunc_tbl_rels_b.c.organisationfunktion_registrering_id
            == orgfunc_tbl_rels_a.c.organisationfunktion_registrering_id,
        )
        .where(
            orgfunc_tbl_rels_a.c.rel_maal_uuid != None,  # noqa: E711
            orgfunc_tbl_rels_a.c.rel_type == "tilknyttedeenheder",
            orgfunc_tbl_rels_b.c.rel_maal_urn != None,  # noqa: E711
            orgfunc_tbl_rels_b.c.rel_type == "adresser",
            orgfunc_tbl_rels_b.c.rel_maal_urn.ilike(search_phrase),
            text(
                f"(organisationfunktion_relation_1.virkning).timeperiod @> {at_datetime_str_sql}"
            ),
        )
        .cte()
    )


def _orgunit_rel_itsystems_hits_query(
    orgfunc_tbl_rels, orgfunc_tbl_attrs, search_phrase: str, at_datetime_str_sql: str
):
    orgfunc_orgunit_uuid_col = orgfunc_tbl_rels.c.rel_maal_uuid.label("uuid")

    return (
        select(orgfunc_orgunit_uuid_col)
        .outerjoin(
            orgfunc_tbl_attrs,
            orgfunc_tbl_attrs.c.organisationfunktion_registrering_id
            == orgfunc_tbl_rels.c.organisationfunktion_registrering_id,
        )
        .where(
            orgfunc_tbl_rels.c.rel_maal_uuid != None,  # noqa: E711
            orgfunc_tbl_rels.c.rel_type == "tilknyttedeenheder",
            orgfunc_tbl_attrs.c.funktionsnavn == "Adresse",
            orgfunc_tbl_attrs.c.brugervendtnoegle.ilike(search_phrase),
            text(
                f"(organisationfunktion_relation.virkning).timeperiod @> {at_datetime_str_sql}"
            ),
        )
        .cte()
    )


def _org_unit_path(engine, all_hits, enhed_uuid, at_datetime_str_sql: str):
    # Construct a scalar subselect which will return the path for each found
    # org unit in `all_hits`.

    org = get_table("organisation", engine)
    enhed_reg = get_table("organisationenhed_registrering", engine)
    enhed_rel = get_table("organisationenhed_relation", engine)
    enhed_att = get_table("organisationenhed_attr_egenskaber", engine)

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
            text(
                f"(organisationenhed_relation.virkning).timeperiod @> {at_datetime_str_sql}"
            ),
            text(
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_datetime_str_sql}"
            ),
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


# SQLAlchemy methods


def get_table(name, engine):
    """Return SQLAlchemy `Table` instance of SQL table"""
    return Table(name, MetaData(schema="actual_state"), autoload_with=engine)


async def load_table(name, async_engine):
    metadata = MetaData(schema="actual_state")
    table = Table(name, metadata)

    # async with async_engine.connect() as conn:
    #     await conn.run_sync(table.reflect)
    async with async_engine.connect() as conn:
        await conn.run_sync(metadata.reflect, kw={"bind": conn, "only": [name]})

    return table


def get_engine():
    """Return SQLAlchemy `Engine` instance bound to the LoRa database"""
    password = "mysecretpassword"
    return create_engine(f"postgresql://postgres:{password}@mox-db:5432/mox")


def execute_query(query, engine, limit=1000):
    """Run SQLAlchemy query with a default LIMIT of 1000"""
    with engine.connect() as conn:
        result = conn.execute(query.limit(limit))
        rows = result.mappings().fetchall()
        return rows
