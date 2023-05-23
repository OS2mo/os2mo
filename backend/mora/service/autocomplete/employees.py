# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import cast
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import text
from sqlalchemy.sql import union

from .shared import get_at_date_sql
from .shared import get_graphql_equivalent_by_uuid
from .shared import read_sqlalchemy_result
from .shared import string_to_urn
from .shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora import util
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.graphapi.shim import execute_graphql
from mora.service.util import handle_gql_error


async def search_employees(
    sessionmaker: async_sessionmaker, query: str, at: date | None = None
) -> [Row]:
    at_sql, at_sql_bind_params = get_at_date_sql(at)

    async with sessionmaker() as session:
        selects = [
            select(cte.c.uuid)
            for cte in (
                _get_cte_uuid_hits(query, at_sql),
                _get_cte_name_hits(query, at_sql),
                _get_cte_addr_hits(query, at_sql),
                _get_cte_itsystem_hits(query, at_sql),
            )
        ]
        all_hits = union(*selects).cte()

        employee_id = BrugerRegistrering.bruger_id.label("uuid")
        query_final = (
            select(employee_id)
            .where(employee_id == all_hits.c.uuid)
            .group_by(employee_id)
        )

        # Execute & parse results
        return read_sqlalchemy_result(
            await session.execute(query_final, {**at_sql_bind_params})
        )


async def decorate_employee_search_result(search_results: [Row], at: date | None):
    graphql_vars = {"uuids": [str(employee.uuid) for employee in search_results]}
    if at is not None:
        graphql_vars["from_date"] = at

    from mora.graphapi.versions.v4.version import GraphQLVersion

    employee_decorate_query = """
        query EmployeeDecorate($uuids: [UUID!], $from_date: DateTime) {
          employees(uuids: $uuids, from_date: $from_date) {
            uuid
            objects {
              uuid
              user_key
              cpr_no

              name
              givenname
              surname

              nickname
              nickname_givenname
              nickname_surname

              engagements {
                uuid
                user_key
                engagement_type {
                  uuid
                  name
                  published
                }
              }

              addresses {
                uuid
                user_key
                value
                address_type {
                  uuid
                  name
                  published
                }
              }

              associations {
                uuid
                user_key
                association_type {
                  uuid
                  name
                  published
                }
              }

              itusers {
                uuid
                user_key
                itsystem {
                  uuid
                  name
                }
              }
            }
          }
        }
    """

    response = await execute_graphql(
        employee_decorate_query,
        graphql_version=GraphQLVersion,
        variable_values=jsonable_encoder(graphql_vars),
    )
    handle_gql_error(response)

    decorated_result = []
    for idx, employee in enumerate(search_results):
        graphql_equivalent = get_graphql_equivalent_by_uuid(
            response.data["employees"], employee.uuid
        )
        if not graphql_equivalent:
            continue

        decorated_result.append(
            {
                "uuid": employee.uuid,
                "name": graphql_equivalent["name"],
                "attrs": _gql_get_employee_attrs(graphql_equivalent),
            }
        )

    return decorated_result


def _get_cte_uuid_hits(query: str, at_sql: str):
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
            text(f"(bruger_attr_udvidelser.virkning).timeperiod @> {at_sql}"),
        )
        .cte()
    )


def _get_cte_name_hits(query: str, at_sql: str):
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
            text(f"(bruger_attr_udvidelser.virkning).timeperiod @> {at_sql}"),
        )
        .cte()
    )


def _get_cte_addr_hits(query: str, at_sql: str):
    orgfunc_tbl_rels_1 = aliased(OrganisationFunktionRelation)
    orgfunc_tbl_rels_2 = aliased(OrganisationFunktionRelation)

    query = string_to_urn(query)
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
            text(f"(organisationfunktion_relation_1.virkning).timeperiod @> {at_sql}"),
            cast(orgfunc_tbl_rels_2.rel_type, String)
            == OrganisationFunktionRelationKode.adresser,
            orgfunc_tbl_rels_2.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


def _get_cte_itsystem_hits(query: str, at_sql: str):
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
            text(f"(organisationfunktion_relation.virkning).timeperiod @> {at_sql}"),
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "IT-system",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
        )
        .cte()
    )


def _gql_get_employee_attrs(gql_employee: dict):
    attrs = []

    for engagement in gql_employee.get("engagements", []):
        uuid = engagement["uuid"]
        value = engagement["user_key"]
        engagement_type = engagement.get("engagement_type")
        if not engagement_type:
            continue

        if util.is_detail_unpublished(
            value, engagement_type.get("published")
        ) or util.is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": engagement["engagement_type"]["name"],
                "value": value,
            }
        )

    for address in gql_employee.get("addresses", []):
        uuid = address["uuid"]
        value = address["value"]
        addr_type = address.get("address_type")
        if not addr_type:
            continue

        if util.is_detail_unpublished(
            value, addr_type.get("published")
        ) or util.is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": address["address_type"]["name"],
                "value": value,
            }
        )

    for assoc in gql_employee.get("associations", []):
        uuid = assoc["uuid"]
        value = assoc["user_key"]
        assoc_type = assoc.get("association_type")
        if not assoc_type:
            continue

        if util.is_detail_unpublished(
            value, assoc_type.get("published")
        ) or util.is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": assoc["association_type"]["name"],
                "value": value,
            }
        )

    for ituser in gql_employee.get("itusers", []):
        uuid = ituser["uuid"]
        value = ituser["user_key"]

        if not ituser.get("itsystem"):
            continue

        if util.is_detail_unpublished(value) or util.is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": ituser["itsystem"]["name"],
                "value": value,
            }
        )

    return attrs