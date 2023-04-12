# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from contextlib import suppress
from itertools import starmap
from uuid import UUID

from datetime import date
from datetime import datetime
from datetime import time

from sqlalchemy import cast
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union
from sqlalchemy.sql import text

from mora import common
from mora import util
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


async def search_orgunits(search_phrase: str, at: date | None = None):
    if not search_phrase:
        return {"items": []}

    db_engine = get_engine()

    at_datetime_str_sql = "now()"
    if at is not None:
        at_datetime_str_sql = (
            f"to_timestamp('{datetime.combine(at, time.min).isoformat()}', "
            "'YYYY-MM-DD HH24:MI:SS')"
        )

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
        orgunit_tbl_regs, orgunit_tbl_attrs, orgunit_reg_col_uuid, search_phrase, at_datetime_str_sql
    )
    hits_orgunit_addrs = _orgunit_rel_addr_hits_query(orgfunc_tbl_rels, search_phrase, at_datetime_str_sql)
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
        select(orgunit_reg_col_uuid)
        .where(orgunit_reg_col_uuid == all_hits.c.uuid)
        .group_by(orgunit_reg_col_uuid)
    )

    return execute_query(q, db_engine)


# PRIVATE methods


def _orgunit_uuid_hits_query(
    orgunit_tbl_regs, orgunit_tbl_attrs, search_phrase: str, at_datetime_str_sql: str
):
    # TODO: Do we use the JOIN on "orgunit_tbl_attrs" for anything? looks we can just remove it
    return (
        select(
            orgunit_tbl_regs.c.organisationenhed_id.label("uuid")
        )
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
    orgunit_tbl_regs, orgunit_tbl_attrs, orgunit_reg_col_uuid, search_phrase: str, at_datetime_str_sql: str
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


def _orgunit_rel_addr_hits_query(orgfunc_tbl_rels, search_phrase: str, at_datetime_str_sql: str):
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
            )
        )
        .cte()
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
