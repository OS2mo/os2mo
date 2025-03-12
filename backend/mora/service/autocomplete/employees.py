# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from datetime import date
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import cast
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union

from mora import config
from mora import util
from mora.access_log import access_log
from mora.db import AsyncSession
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.graphapi.shim import execute_graphql
from mora.service.autocomplete.shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora.service.autocomplete.shared import get_at_date_sql
from mora.service.autocomplete.shared import get_graphql_equivalent_by_uuid
from mora.service.autocomplete.shared import read_sqlalchemy_result
from mora.service.autocomplete.shared import string_to_urn
from mora.service.util import handle_gql_error


async def search_employees(
    session: AsyncSession, query: str, at: date | None = None
) -> list[UUID]:
    at_sql, at_sql_bind_params = get_at_date_sql(at)

    ctes = await asyncio.gather(
        _get_cte_uuid_hits(query),
        _get_cte_user_key_hits(query),
        _get_cte_name_hits(query),
        _get_cte_cpr_hits(query),
        _get_cte_addr_hits(query),
        _get_cte_itsystem_hits(query),
    )
    selects = [select(cte.c.uuid) for cte in ctes]
    all_hits = union(*selects).cte()

    employee_id = BrugerRegistrering.bruger_id.label("uuid")
    query_final = (
        select(employee_id).where(employee_id == all_hits.c.uuid).group_by(employee_id)
    )

    # Execute & parse results
    result = read_sqlalchemy_result(
        await session.execute(query_final, {**at_sql_bind_params})
    )
    uuids = [employee.uuid for employee in result]
    access_log(session, "search_employees", "Bruger", {"query": query, "at": at}, uuids)
    return uuids


async def decorate_employee_search_result(
    settings: config.Settings, search_results: list[UUID], at: date | None
):
    graphql_vars = {"uuids": search_results}
    employee_decorate_query = """
        query EmployeeDecorate($uuids: [UUID!]) {
            employees(filter: { uuids: $uuids, from_date: null, to_date: null }) {
                objects {
                    uuid

                    objects {
                        ...employee_details
                    }
                }
            }
        }

        fragment employee_details on Employee {
            uuid
            user_key
            cpr_no
            name
            givenname
            surname
            nickname
            nickname_givenname
            nickname_surname

            validity {
                from
                to
            }
        }
    """

    if settings.confdb_autocomplete_attrs_employee:
        employee_decorate_query = """
            query EmployeeDecorate($uuids: [UUID!]) {
                employees(filter: { uuids: $uuids, from_date: null, to_date: null }) {
                    objects {
                        uuid

                        objects {
                            ...employee_details
                        }
                    }
                }
            }

            fragment employee_details on Employee {
                uuid
                user_key
                cpr_no
                name
                givenname
                surname
                nickname
                nickname_givenname
                nickname_surname

                validity {
                    from
                    to
                }

                engagements(filter: {from_date: null, to_date: null}) {
                    uuid
                    user_key
                    engagement_type(filter: {from_date: null, to_date: null}) {
                        uuid
                        name
                        published
                    }
                }

                addresses(filter: {from_date: null, to_date: null}) {
                    uuid
                    user_key
                    value
                    address_type(filter: {from_date: null, to_date: null}) {
                        uuid
                        name
                        published
                    }
                }

                associations(filter: {from_date: null, to_date: null}){
                    uuid
                    user_key
                    association_type(filter: {from_date: null, to_date: null}) {
                        uuid
                        name
                        published
                    }
                }

                itusers(filter: {from_date: null, to_date: null}) {
                    uuid
                    user_key
                    itsystem(filter: {from_date: null, to_date: null}){
                        uuid
                        name
                    }
                }
            }
        """

    response = await execute_graphql(
        employee_decorate_query,
        variable_values=jsonable_encoder(graphql_vars),
    )
    handle_gql_error(response)

    decorated_result = []
    for employee_uuid in search_results:
        graphql_equivalent = get_graphql_equivalent_by_uuid(
            response.data["employees"]["objects"], employee_uuid, at
        )
        if not graphql_equivalent:  # pragma: no cover
            continue

        decorated_result.append(
            {
                "uuid": employee_uuid,
                "name": graphql_equivalent["name"],
                "attrs": _gql_get_employee_attrs(settings, graphql_equivalent),
            }
        )

    return decorated_result


async def _get_cte_uuid_hits(query: str):
    search_phrase = util.query_to_search_phrase(query)

    return (
        select(BrugerRegistrering.bruger_id.label("uuid"))
        .join(
            # OBS: We join on this table to get validity of the UUID
            # QUESTION: Should we change this join on "BrugerAttrEgenskaber" where the BVN resides,
            # which should work as an alias for the UUID ?
            BrugerAttrUdvidelser,
            BrugerAttrUdvidelser.bruger_registrering_id == BrugerRegistrering.id,
        )
        .where(
            func.char_length(search_phrase) > UUID_SEARCH_MIN_PHRASE_LENGTH,
            BrugerRegistrering.bruger_id != None,  # noqa: E711
            cast(BrugerRegistrering.bruger_id, Text).ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_name_hits(query: str):
    search_phrase = util.query_to_search_phrase(query)

    name_concated = func.concat(
        BrugerAttrUdvidelser.fornavn,
        " ",
        BrugerAttrUdvidelser.efternavn,
        " ",
        BrugerAttrUdvidelser.kaldenavn_fornavn,
        " ",
        BrugerAttrUdvidelser.kaldenavn_efternavn,
    )

    return (
        select(BrugerRegistrering.bruger_id.label("uuid"))
        .join(
            BrugerAttrUdvidelser,
            BrugerAttrUdvidelser.bruger_registrering_id == BrugerRegistrering.id,
        )
        .where(
            BrugerRegistrering.bruger_id != None,  # noqa: E711
            name_concated.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_cpr_hits(query: str):
    # NOTE: CPR is persisted as a URN in the relation tabel
    query = await string_to_urn(query)
    search_phrase = util.query_to_search_phrase(query)

    return (
        select(BrugerRegistrering.bruger_id.label("uuid"))
        .join(
            BrugerRelation,
            BrugerRelation.bruger_registrering_id == BrugerRegistrering.id,
        )
        .where(
            BrugerRegistrering.bruger_id != None,  # noqa: E711
            BrugerRelation.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_addr_hits(query: str):
    orgfunc_tbl_rels_1 = aliased(OrganisationFunktionRelation)
    orgfunc_tbl_rels_2 = aliased(OrganisationFunktionRelation)

    query = await string_to_urn(query)
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
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            cast(orgfunc_tbl_rels_2.rel_type, String)
            == OrganisationFunktionRelationKode.adresser,
            orgfunc_tbl_rels_2.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_itsystem_hits(query: str):
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
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "IT-system",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_user_key_hits(query: str):
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
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "Engagement",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
        )
        .cte()
    )


def _gql_get_employee_attrs(settings: config.Settings, gql_employee: dict):
    attrs = []

    for engagement in gql_employee.get("engagements", []):
        uuid = engagement["uuid"]
        value = engagement["user_key"]
        engagement_type = engagement.get("engagement_type")
        if (
            not engagement_type
            or UUID(engagement_type["uuid"])
            not in settings.confdb_autocomplete_attrs_employee
        ):  # pragma: no cover
            continue

        if util.is_detail_unpublished(
            value, engagement_type.get("published")
        ) or util.is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": engagement_type["name"],
                "value": value,
            }
        )

    for address in gql_employee.get("addresses", []):
        uuid = address["uuid"]
        value = address["value"]
        addr_type = address.get("address_type")
        if (
            not addr_type
            or UUID(addr_type["uuid"])
            not in settings.confdb_autocomplete_attrs_employee
        ):
            continue

        if util.is_detail_unpublished(
            value, addr_type.get("published")
        ) or util.is_uuid(value):  # pragma: no cover
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": addr_type["name"],
                "value": value,
            }
        )

    for assoc in gql_employee.get("associations", []):
        uuid = assoc["uuid"]
        value = assoc["user_key"]
        assoc_type = assoc.get("association_type")
        if (
            not assoc_type
            or UUID(assoc_type["uuid"])
            not in settings.confdb_autocomplete_attrs_employee
        ):  # pragma: no cover
            continue

        if util.is_detail_unpublished(
            value, assoc_type.get("published")
        ) or util.is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": assoc_type["name"],
                "value": value,
            }
        )

    for ituser in gql_employee.get("itusers", []):
        uuid = ituser["uuid"]
        value = ituser["user_key"]
        itsystem = ituser.get("itsystem")
        if (
            not itsystem
            or UUID(itsystem["uuid"]) not in settings.confdb_autocomplete_attrs_employee
        ):  # pragma: no cover
            continue

        if util.is_detail_unpublished(value):  # pragma: no cover
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": itsystem["name"],
                "value": value,
            }
        )

    return attrs
