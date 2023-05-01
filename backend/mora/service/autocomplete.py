# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from contextlib import suppress
from datetime import date
from itertools import starmap
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from more_itertools import one
from sqlalchemy import cast
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.result import Result
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql import literal_column
from sqlalchemy.sql import select
from sqlalchemy.sql import text
from sqlalchemy.sql import union

from mora import common
from mora import config
from mora import util
from mora.db import Organisation
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationEnhedRelation
from mora.db import OrganisationEnhedRelationKode
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.graphapi.shim import execute_graphql
from mora.lora import AutocompleteScope
from mora.service.util import handle_gql_error


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


async def search_orgunits(
    sessionmaker: async_sessionmaker, query: str, at: date | None = None
) -> [Row]:
    at_sql, at_sql_bind_params = _get_at_date_sql(at)

    async with sessionmaker() as session:
        selects = [
            select(cte.c.uuid)
            for cte in (
                _get_cte_orgunit_uuid_hits(query, at_sql),
                _get_cte_orgunit_name_hits(query, at_sql),
                _get_cte_orgunit_addr_hits(query, at_sql),
                _get_cte_orgunit_itsystem_hits(query, at_sql),
            )
        ]
        all_hits = union(*selects).cte()

        query_final = (
            select(
                OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"),
                _org_unit_path(
                    all_hits,
                    OrganisationEnhedRegistrering.organisationenhed_id,
                    at_sql,
                ).label("path"),
            )
            .where(
                OrganisationEnhedRegistrering.organisationenhed_id == all_hits.c.uuid
            )
            .group_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )

        # Execute & parse results
        return _read_sqlalchemy_result(
            await session.execute(query_final, {**at_sql_bind_params})
        )


async def decorate_orgunit_search_result(
    settings: config.Settings, search_results: [Row], at: date | None
):
    graphql_vars = {"uuids": [str(orgunit.uuid) for orgunit in search_results]}
    if at is not None:
        graphql_vars["from_date"] = at

    orgunit_decorate_query = """
            query OrgUnitDecorate($uuids: [UUID!], $from_date: DateTime) {
                org_units(uuids: $uuids, from_date: $from_date) {
                    uuid
                    objects {
                        name
                        user_key
                        uuid
                        parent_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
            """
    if settings.confdb_autocomplete_attrs_orgunit:
        orgunit_decorate_query = """
            query OrgUnitDecorate($uuids: [UUID!], $from_date: DateTime) {
                org_units(uuids: $uuids, from_date: $from_date) {
                    uuid
                    objects {
                        name
                        user_key
                        uuid
                        parent_uuid
                        validity {
                            from
                            to
                        }

                        addresses {
                            uuid
                            name
                            address_type {
                                uuid
                                name
                            }
                        }

                        itusers {
                            uuid
                            user_key
                            itsystem {
                              uuid
                              user_key
                              name
                            }
                        }
                    }
                }
            }
            """

    response = await execute_graphql(
        orgunit_decorate_query, variable_values=jsonable_encoder(graphql_vars)
    )
    handle_gql_error(response)

    decorated_result = []
    for idx, orgunit in enumerate(search_results):
        graphql_equivilent = _get_graphql_equivalent(response, orgunit.uuid)
        if not graphql_equivilent:
            continue

        attrs = _gql_get_orgunit_attrs(settings, graphql_equivilent)
        decorated_result.append(
            {
                "uuid": orgunit.uuid,
                "name": graphql_equivilent["name"],
                "path": orgunit.path,
                "attrs": attrs,
            }
        )

    return decorated_result


def _get_graphql_equivalent(graphql_response, org_unit_uuid: UUID) -> dict | None:
    for graphql_orgunit in graphql_response.data["org_units"]:
        if graphql_orgunit["uuid"] == str(org_unit_uuid):
            return one(graphql_orgunit["objects"])

    return None


def _gql_get_orgunit_attrs(settings: config.Settings, org_unit_graphql: dict) -> [dict]:
    attrs: [dict] = []
    if "addresses" in org_unit_graphql:
        for addr in org_unit_graphql["addresses"]:
            if (
                UUID(addr["address_type"]["uuid"])
                not in settings.confdb_autocomplete_attrs_orgunit
            ):
                continue

            attrs.append(
                {
                    "uuid": UUID(addr["uuid"]),
                    "value": addr["name"],
                    "title": addr["address_type"]["name"],
                }
            )

    if "itusers" in org_unit_graphql:
        for ituser in org_unit_graphql["itusers"]:
            if (
                UUID(ituser["itsystem"]["uuid"])
                not in settings.confdb_autocomplete_attrs_orgunit
            ):
                continue

            attrs.append(
                {
                    "uuid": UUID(ituser["uuid"]),
                    "value": ituser["user_key"],
                    "title": ituser["itsystem"]["name"],
                }
            )

    return attrs


def _read_sqlalchemy_result(result: Result) -> [Row]:
    rows = []
    while True:
        chunk = result.fetchmany(1000)
        if not chunk:
            break

        for row in chunk:
            rows.append(row)

    return rows


def _get_at_date_sql(at: date | None = None):
    if at is not None:
        return "to_timestamp(:at_datetime, 'YYYY-MM-DD HH24:MI:SS')", {
            "at_datetime": at.isoformat()
        }

    return "now()", {}


def _get_cte_orgunit_uuid_hits(query: str, at_sql: str):
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
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_sql}"
                # f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> to_timestamp(:sql_at_datetime, 'YYYY-MM-DD HH24:MI:SS')"
            ),
        )
        .cte()
    )


def _get_cte_orgunit_name_hits(query: str, at_sql: str):
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
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_sql}"
            ),
        )
        .cte()
    )


def _get_cte_orgunit_addr_hits(query: str, at_sql: str):
    orgfunc_tbl_rels_1 = aliased(OrganisationFunktionRelation)
    orgfunc_tbl_rels_2 = aliased(OrganisationFunktionRelation)

    query = util.urnquote(
        query.lower()
    )  # since we are search through "rel_maal_urn"-cols
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
            text(f"(organisationfunktion_relation_1.virkning).timeperiod @> {at_sql}"),
            cast(orgfunc_tbl_rels_2.rel_type, String)
            == OrganisationFunktionRelationKode.adresser,
            orgfunc_tbl_rels_2.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


def _get_cte_orgunit_itsystem_hits(query: str, at_sql: str):
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
            text(f"(organisationfunktion_relation.virkning).timeperiod @> {at_sql}"),
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "IT-system",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
        )
        .cte()
    )


def _org_unit_path(all_hits, enhed_uuid, at_sql: str):
    nodes_cte = select(
        # "Base" org unit UUID (same for all rows in result)
        all_hits.c.uuid.label("base_id"),
        # Current org unit UUID (different for each row in result)
        all_hits.c.uuid.label("id"),
        # Empty array of strings (will be populated the in accumulative CTE
        # below.)
        literal_column("array[]::text[]").label("p"),
    ).cte(recursive=True)

    nodes_recursive = nodes_cte.alias()
    nodes_cte = nodes_cte.union(
        select(
            # Keep the UUID of the base org unit (same for all rows in CTE)
            nodes_recursive.columns.base_id,
            # Record the UUID of the current parent org unit
            OrganisationEnhedRelation.rel_maal_uuid,
            # Prepend the name of the current org unit onto path 'p'
            func.array_prepend(
                OrganisationEnhedAttrEgenskaber.enhedsnavn, nodes_recursive.columns.p
            ),
        )
        .join(
            OrganisationEnhedRegistrering,
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
        )
        .join(
            OrganisationEnhedAttrEgenskaber,
            OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
            == OrganisationEnhedRegistrering.id,
        )
        .join(
            nodes_recursive,
            nodes_recursive.columns.id
            == OrganisationEnhedRegistrering.organisationenhed_id,
        )
        .where(
            # OrganisationEnhedRelation.rel_type == "overordnet",
            cast(OrganisationEnhedRelation.rel_type, String)
            == OrganisationEnhedRelationKode.overordnet,
            text(f"(organisationenhed_relation.virkning).timeperiod @> {at_sql}"),
            text(
                f"(organisationenhed_attr_egenskaber.virkning).timeperiod @> {at_sql}"
            ),
        )
    )

    return (
        # Take first *complete* path (only 1 is expected)
        select(func.json_agg(nodes_cte.columns.p, type_=postgresql.JSONB)[0]).where(
            # A complete path must start at the current org unit UUID
            nodes_cte.columns.base_id == enhed_uuid,
            # A complete path must contain the root org unit UUID
            nodes_cte.columns.id.in_(select(Organisation.id)),
        )
    )
