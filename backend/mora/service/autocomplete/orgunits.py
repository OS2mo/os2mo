# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Select
from sqlalchemy import Text
from sqlalchemy import Tuple
from sqlalchemy import cast
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union

from mora import config
from mora import util
from mora.access_log import access_log
from mora.db import AsyncSession
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db._common import LivscyklusKode
from mora.graphapi.shim import execute_graphql
from mora.service.autocomplete.shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora.service.autocomplete.shared import get_at_date_sql
from mora.service.autocomplete.shared import get_graphql_equivalent_by_uuid
from mora.service.autocomplete.shared import read_sqlalchemy_result
from mora.service.util import handle_gql_error


def search_orgunits_query(
    query: str,
    at: date | None = None,
) -> Select[Tuple]:
    at_sql, _ = get_at_date_sql(at)
    return _sqlalchemy_generate_query(query, at_sql)


async def search_orgunits(
    session: AsyncSession, query: str, at: date | None = None
) -> list[UUID]:
    _, at_sql_bind_params = get_at_date_sql(at)
    query_final = search_orgunits_query(query, at)
    # Execute & parse results
    result = read_sqlalchemy_result(
        await session.execute(query_final, {**at_sql_bind_params})
    )
    uuids = [orgunit.uuid for orgunit in result]
    access_log(
        session,
        "search_orgunits",
        "OrganisationEnhed",
        {"query": query, "at": at},
        uuids,
    )
    return uuids


async def decorate_orgunit_search_result(
    settings: config.Settings, search_results: list[UUID], at: date | None
):
    graphql_vars = {"uuids": search_results}
    if at is not None:
        graphql_vars["from_date"] = at

    orgunit_decorate_query = """
        query OrgUnitDecorate($uuids: [UUID!], $from_date: DateTime) {
            org_units(filter: { uuids: $uuids, from_date: $from_date, to_date: null }) {
                objects {
                    uuid

                    objects {
                        ...orgunit_details
                    }
                }
            }
        }

        fragment orgunit_details on OrganisationUnit {
            uuid
            name
            user_key

            validity {
                from
                to
            }

            ancestors_validity {
                name
            }
        }
        """

    if settings.confdb_autocomplete_attrs_orgunit:
        orgunit_decorate_query = """
            query OrgUnitDecorate($uuids: [UUID!], $from_date: DateTime) {
                org_units(filter: { uuids: $uuids, from_date: $from_date, to_date: null }) {
                    objects {
                        uuid

                        current {
                            ...orgunit_details
                        }

                        objects {
                            ...orgunit_details
                        }
                    }
                }
            }

            fragment orgunit_details on OrganisationUnit {
                uuid
                name
                user_key

                validity {
                    from
                    to
                }

                ancestors_validity {
                    name
                }

                addresses(filter: {from_date: $from_date, to_date: null}) {
                    uuid
                    name
                    address_type(filter: {from_date: $from_date, to_date: null}) {
                        uuid
                        name
                    }
                }

                itusers(filter: {from_date: $from_date, to_date: null}) {
                    uuid
                    user_key
                    itsystem(filter: {from_date: $from_date, to_date: null}) {
                        uuid
                        user_key
                        name
                    }
                }
            }
            """

    response = await execute_graphql(
        orgunit_decorate_query,
        variable_values=jsonable_encoder(graphql_vars),
    )
    handle_gql_error(response)

    decorated_result = []
    for orgunit_uuid in search_results:
        graphql_equivalent = get_graphql_equivalent_by_uuid(
            response.data["org_units"]["objects"], orgunit_uuid, at
        )
        if not graphql_equivalent:  # pragma: no cover
            continue

        decorated_result.append(
            {
                "uuid": orgunit_uuid,
                "name": graphql_equivalent["name"],
                "path": _gql_get_orgunit_path(graphql_equivalent),
                "attrs": _gql_get_orgunit_attrs(settings, graphql_equivalent),
                "validity": graphql_equivalent["validity"],
            }
        )

    return decorated_result


def _sqlalchemy_generate_query(query: str, at_sql: str) -> Select[Tuple]:
    selects = [
        select(cte.c.uuid)
        for cte in (
            _get_cte_orgunit_uuid_hits(query, at_sql),
            _get_cte_orgunit_name_hits(query, at_sql),
        )
    ]
    all_hits = union(*selects).cte()

    query_final = (
        select(
            OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"),
        )
        .where(OrganisationEnhedRegistrering.organisationenhed_id == all_hits.c.uuid)
        .group_by(OrganisationEnhedRegistrering.organisationenhed_id)
    )

    return query_final


def _gql_get_orgunit_attrs(settings: config.Settings, org_unit_graphql: dict) -> [dict]:
    attrs: [dict] = []
    if "addresses" in org_unit_graphql:
        for addr in org_unit_graphql["addresses"]:
            address_type = addr["address_type"]
            if (
                UUID(address_type["uuid"])
                not in settings.confdb_autocomplete_attrs_orgunit
            ):
                continue

            attrs.append(
                {
                    "uuid": UUID(addr["uuid"]),
                    "value": addr["name"],
                    "title": address_type["name"],
                }
            )

    if "itusers" in org_unit_graphql:
        for ituser in org_unit_graphql["itusers"]:
            itsystem = ituser["itsystem"]
            if (
                UUID(itsystem["uuid"]) not in settings.confdb_autocomplete_attrs_orgunit
            ):  # pragma: no cover
                continue

            attrs.append(
                {
                    "uuid": UUID(ituser["uuid"]),
                    "value": ituser["user_key"],
                    "title": itsystem["name"],
                }
            )

    return attrs


def _gql_get_orgunit_path(org_unit_graphql: dict):
    if not org_unit_graphql.get("ancestors_validity", []):
        return []

    path = [x["name"] for x in reversed(org_unit_graphql["ancestors_validity"])]
    return path + [org_unit_graphql["name"]]


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
            OrganisationEnhedRegistrering.lifecycle != cast("Slettet", LivscyklusKode),
            OrganisationEnhedRegistrering.registrering_period.contains(func.now()),
            func.char_length(search_phrase) > UUID_SEARCH_MIN_PHRASE_LENGTH,
            OrganisationEnhedRegistrering.organisationenhed_id != None,  # noqa: E711
            cast(OrganisationEnhedRegistrering.organisationenhed_id, Text).ilike(
                search_phrase
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
            OrganisationEnhedRegistrering.lifecycle != cast("Slettet", LivscyklusKode),
            OrganisationEnhedRegistrering.registrering_period.contains(func.now()),
            OrganisationEnhedRegistrering.organisationenhed_id != None,  # noqa: E711
            (
                OrganisationEnhedAttrEgenskaber.enhedsnavn.ilike(search_phrase)
                | OrganisationEnhedAttrEgenskaber.brugervendtnoegle.ilike(search_phrase)
            ),
        )
        .cte()
    )
