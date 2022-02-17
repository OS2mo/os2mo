# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from datetime import datetime
from typing import Any
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from more_itertools import flatten
from more_itertools import one
from pydantic import root_validator
from ramodels.mo import EmployeeRead
from ramodels.mo import OrganisationRead

from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.service.employee import router as employee_router
from mora.service.itsystem import router as it_router

# --------------------------------------------------------------------------------------
# Auxiliary functions
# --------------------------------------------------------------------------------------


def flatten_data(resp_dict: dict[str, Any]):
    return list(flatten([d["objects"] for d in resp_dict]))


# --------------------------------------------------------------------------------------
# Shimmed endpoints
# --------------------------------------------------------------------------------------


class MOEmployee(EmployeeRead):
    name: str
    nickname: str
    org: OrganisationRead
    validity: Optional[Any]  # not part of the "old" MO response

    @root_validator(pre=True)
    def handle_deprecated_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        # noop overriding parent method - we need name & nickname
        return values


@employee_router.get(
    "/e/{id}/",
    response_model=Union[MOEmployee, UUID],
    response_model_exclude_unset=True,
)
async def get_employee(
    id: UUID,
    only_primary_uuid: Optional[bool] = None,
    at: Optional[Union[date, datetime]] = None,
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
            employee = one(employees)
            return {
                **employee,
                "org": r.data["org"],
            }

    dates = dict()
    if at is not None:
        dates["from_date"] = at
    variables = {"uuid": id, **dates}
    # Execute GraphQL query to fetch required data
    r = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )
    if r.errors:
        raise ValueError(r.errors)
    if not flatten_data(r.data["employees"]):
        exceptions.ErrorCodes.E_USER_NOT_FOUND()
    # Transform graphql data into the original format
    return transformer(r.data)


def meta_router():
    router = APIRouter()

    @router.get("/version/")
    async def version():
        query = """
        query VersionQuery {
          version {
            mo_hash
            lora_version
            mo_version
          }
        }
        """

        # Execute GraphQL query to fetch required data
        r = await execute_graphql(query)
        if r.errors:
            raise ValueError(r.errors)

        return r.data["version"]

    @router.get("/service/{rest_of_path:path}")
    def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    return router


@it_router.get("/o/{orgid}/it/")
async def list_it_systems(orgid: UUID):
    """List the IT systems available within the given organisation.

    :param orgid: Restrict search to this organisation.

    .. :quickref: IT system; List available systems

    :>jsonarr string uuid: The universally unique identifier of the system.
    :>jsonarr string name: The name of the system.
    :>jsonarr string system_type: The type of the system.
    :>jsonarr string user_key: A human-readable unique key for the system.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Lokal Rammearkitektur",
          "system_type": null,
          "user_key": "LoRa",
          "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
        },
        {
          "name": "Active Directory",
          "system_type": null,
          "user_key": "AD",
          "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"
        }
      ]

    """
    orgid = str(orgid)

    query = """
    query ITSystemQuery {
      itsystems {
        objects { uuid, name, system_type, user_key }
      }
      org {
        uuid
      }
    }
    """
    r = await execute_graphql(query)
    if r.errors:
        raise ValueError(r.errors)
    if r.data["org"]["uuid"] != orgid:
        return []
    return flatten_data(r.data["itsystems"])
