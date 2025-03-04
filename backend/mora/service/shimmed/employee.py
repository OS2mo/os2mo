# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import Body
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from mora import exceptions
from mora import util
from mora.auth.keycloak import oidc
from mora.graphapi.shim import MOEmployee
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.service.employee import router as employee_router

from .errors import handle_gql_error


@employee_router.get(
    "/e/{id}/",
    response_model=MOEmployee | dict[str, UUID],
    response_model_exclude_unset=True,
)
async def get_employee(
    id: UUID = Path(..., description="UUID of the employee to retrieve"),
    only_primary_uuid: bool | None = Query(None, description="Only retrieve the UUID"),
    at: date | datetime | None = Query(
        None, description="Show the employee at this point in time, in ISO-8601 format."
    ),
):
    """Retrieve an employee."""
    if only_primary_uuid:  # pragma: no cover
        query = """
            query GetEmployee($uuid: UUID!, $from_date: DateTime) {
              employees(filter: {uuids: [$uuid], from_date: $from_date}) {
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
              employees(filter: {uuids: [$uuid], from_date: $from_date}) {
                objects {
                  objects {
                    uuid, user_key, cpr_no
                    givenname, surname, name
                    nickname_givenname, nickname_surname, nickname
                    seniority
                  }
                }
              }
              org {
                uuid, user_key, name
              }
            }
        """

        def transformer(data: dict[str, Any]) -> dict[str, Any]:
            employees = flatten_data(data["employees"]["objects"])
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
    if not flatten_data(response.data["employees"]["objects"]):
        exceptions.ErrorCodes.E_USER_NOT_FOUND()
    # Transform graphql data into the original format
    return transformer(response.data)


@employee_router.post(
    "/e/{uuid}/terminate",
    responses={
        "400": {"description": "Invalid input"},
    },
    dependencies=[Depends(oidc.rbac_owner)],
)
async def terminate_employee(uuid: UUID, request: dict = Body(...)):
    """Terminates an employee and all of his roles beginning at a
    specified date. Except for the manager roles, which we vacate
    instead.

    .. :quickref: Employee; Terminate

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: The termination succeeded.

    :param uuid: The UUID of the employee to be terminated.

    :<json string to: When the termination should occur, as an ISO 8601 date.
    :<json boolean vacate: *Optional* - mark applicable — currently
        only ``manager`` -- functions as _vacant_, i.e. simply detach
        the employee from them.

    **Example Request**:

    .. sourcecode:: json

      {
        "validity": {
          "to": "2015-12-31"
        }
      }

    """
    mutation = """
        mutation TerminateEmployee($input: EmployeeTerminateInput!) {
            employee_terminate(input: $input) {
                uuid
            }
        }
    """

    variables = {
        "input": {
            "uuid": uuid,
            "from": request["validity"].get("from"),
            "to": request["validity"].get("to"),
            "vacate": util.checked_get(request, "vacate", False),
        }
    }
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(
        mutation,
        variable_values=jsonable_encoder(variables),
    )
    # coverage: pause
    handle_gql_error(response)
    uuid = response.data["employee_terminate"]["uuid"]
    return uuid
    # coverage: unpause
