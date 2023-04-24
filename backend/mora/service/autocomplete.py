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
from mora.db import OrganisationFunktionAttrEgenskaber
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


async def search_orgunits(sessionmaker, query: str, at: date | None = None):
    sql_at_datetime = _get_at_date_sql(at)

    async with sessionmaker() as session:
        cte_uuid_hits = _get_cte_orgunit_uuid_hits(query, sql_at_datetime)
        cte_name_hits = _get_cte_orgunit_name_hits(query, sql_at_datetime)
        cte_addr_hits = _get_cte_orgunit_addr_hits(query, sql_at_datetime)
        cte_itsystems_hits = _get_cte_orgunit_itsystem_hits(query, sql_at_datetime)

        # UNION all the queries
        selects = [
            select(cte.c.uuid)
            for cte in (
                cte_uuid_hits,
                cte_name_hits,
                cte_addr_hits,
                cte_itsystems_hits,
            )
        ]
        all_hits = union(*selects).cte()

        # FINAL query
        query_final = (
            select(
                OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"),
                # _org_unit_path(all_hits, OrganisationEnhedRegistrering.organisationenhed_id, sql_at_datetime).label("path"),
            )
            .where(
                OrganisationEnhedRegistrering.organisationenhed_id == all_hits.c.uuid
            )
            .group_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )

        # Execute & parse results
        return _read_gql_response(await session.execute(query_final))


# PRIVATE methods


def _read_gql_response(response):
    result = []
    while True:
        chunk = response.fetchmany(1000)
        if not chunk:
            break

        for row in chunk:
            result.append(row)

    return result


def _get_at_date_sql(at: date | None = None):
    sql_at_datetime = "now()"
    if at is not None:
        sql_at_datetime = (
            f"to_timestamp('{datetime.combine(at, time.min).isoformat()}', "
            "'YYYY-MM-DD HH24:MI:SS')"
        )

    return sql_at_datetime


def _get_cte_orgunit_uuid_hits(query: str, sql_at_datetime: str):
    search_phrase = util.query_to_search_phrase(query)
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


def _get_cte_orgunit_name_hits(query: str, sql_at_datetime: str):
    search_phrase = util.query_to_search_phrase(query)
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


def _get_cte_orgunit_addr_hits(query: str, sql_at_datetime: str):
    orgfunc_tbl_rels_1 = aliased(OrganisationFunktionRelation)
    orgfunc_tbl_rels_2 = aliased(OrganisationFunktionRelation)

    query = util.urnquote(query)  # since we are search through "rel_maal_urn"-cols
    search_phrase = util.query_to_search_phrase(query)

    return (
        select(orgfunc_tbl_rels_1.rel_maal_uuid.label("uuid"))
        .outerjoin(
            orgfunc_tbl_rels_2,
            orgfunc_tbl_rels_2.organisationfunktion_registrering_id
            == orgfunc_tbl_rels_1.organisationfunktion_registrering_id,
        )
        .where(
            orgfunc_tbl_rels_1.rel_maal_uuid != None,  # noqa: E711
            cast(orgfunc_tbl_rels_1.rel_type, String)
            == OrganisationFunktionRelationKode.tilknyttedeenheder,
            text(
                f"(organisationfunktion_relation_1.virkning).timeperiod @> {sql_at_datetime}"
            ),
            cast(orgfunc_tbl_rels_2.rel_type, String)
            == OrganisationFunktionRelationKode.adresser,
            orgfunc_tbl_rels_2.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


def _get_cte_orgunit_itsystem_hits(query: str, sql_at_datetime: str):
    search_phrase = util.query_to_search_phrase(query)
    return (
        select(OrganisationFunktionRelation.rel_maal_uuid.label("uuid"))
        .outerjoin(
            OrganisationFunktionAttrEgenskaber,
            OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            == OrganisationFunktionRelation.organisationfunktion_registrering_id,
        )
        .where(
            OrganisationFunktionRelation.rel_maal_uuid != None,  # noqa: E711
            cast(OrganisationFunktionRelation.rel_type, String)
            == OrganisationFunktionRelationKode.tilknyttedeenheder,
            text(
                f"(organisationfunktion_relation.virkning).timeperiod @> {sql_at_datetime}"
            ),
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "IT-system",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
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
