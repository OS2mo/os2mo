# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from .errors import handle_gql_error
from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.shim import MOEmployee
from mora.service.employee import router as employee_router


@employee_router.get(
    "/e/{id}/",
    response_model=MOEmployee | dict[str, UUID],
    response_model_exclude_unset=True,
)
async def get_employee(
    id: UUID = Path(..., description="UUID of the employee to retrieve"),
    only_primary_uuid: bool | None = Query(None, description="Only retrieve the UUID"),
    at: date
    | datetime
    | None = Query(
        None, description="Show the employee at this point in time, in ISO-8601 format."
    ),
):
    """Retrieve an employee."""
    if only_primary_uuid:
        query = """
            query GetEmployee($uuid: UUID!, $from_date: DateTime) {
              employees(uuids: [$uuid], from_date: $from_date) {
            objects { uuid }
          }
        }
        """

        def transformer(data: dict[str, Any]) -> dict[str, Any]:
            employees = flatten_data(data["employees"])
            employee = one(employees)
            return employee

    else:
        query = """
            query GetEmployee($uuid: UUID!, $from_date: DateTime) {
                employees(uuids: [$uuid], from_date: $from_date) {
            objects {
              uuid, user_key, cpr_no
              givenname, surname, name
              nickname_givenname, nickname_surname, nickname
                        seniority
            }
          }
          org {
            uuid, user_key, name
          }
        }
        """

        def transformer(data: dict[str, Any]) -> dict[str, Any]:
            employees = flatten_data(data["employees"])
            print("qqqqqqqqqqqqqqqq", employees)
            employee = one(employees)
            return {
                **employee,
                "org": data["org"],
            }

    dates = {}
    if at is not None:
        dates["from_date"] = at
    variables = {"uuid": id, **dates}
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )
    handle_gql_error(response)
    if not flatten_data(response.data["employees"]):
        print("1111111111111111111111111111")
        exceptions.ErrorCodes.E_USER_NOT_FOUND()
    # Transform graphql data into the original format
    return transformer(response.data)
