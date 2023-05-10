# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import cast
from sqlalchemy import Text
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union

from .shared import get_at_date_sql
from .shared import get_graphql_equivalent_by_uuid
from .shared import read_sqlalchemy_result
from .shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora import util
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
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
                # _get_cte_orgunit_name_hits(query, at_sql),
                # _get_cte_orgunit_addr_hits(query, at_sql),
                # _get_cte_orgunit_itsystem_hits(query, at_sql),
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
                }
              }

              addresses {
                uuid
                user_key
                value
                address_type {
                  uuid
                  name
                }
              }

              associations {
                uuid
                user_key
                association_type {
                  uuid
                  name
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
        employee_decorate_query, variable_values=jsonable_encoder(graphql_vars)
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


def _gql_get_employee_attrs(gql_employee: dict):
    attrs = []

    for engagement in gql_employee.get("engagements", []):
        uuid = engagement["uuid"]
        value = engagement["user_key"]
        if _is_unpublished(value) or _is_uuid(value):
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
        if _is_unpublished(value) or _is_uuid(value):
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
        if _is_unpublished(value) or _is_uuid(value):
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
        if _is_unpublished(value) or _is_uuid(value):
            continue

        attrs.append(
            {
                "uuid": UUID(uuid),
                "title": ituser["itsystem"]["name"],
                "value": value,
            }
        )

    return attrs


def _is_unpublished(v: str):
    return v == "-"


def _is_uuid(v: str):
    try:
        UUID(v)
        return True
    except ValueError:
        return False
