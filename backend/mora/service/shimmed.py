# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from collections.abc import Iterable
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import ilen
from more_itertools import one
from pydantic import root_validator
from ramodels.mo import EmployeeRead
from ramodels.mo import OrganisationRead
from ramodels.mo import OrganisationUnitRead

from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.service.employee import router as employee_router
from mora.service.itsystem import router as it_router
from mora.service.org import router as org_router

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
    response_model=Union[MOEmployee, dict[str, UUID]],
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
        uuid, name, system_type, user_key
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
    return r.data["itsystems"]


@org_router.get(
    "/o/",
    response_model=list[OrganisationRead],
    response_model_exclude_unset=True,
)
async def list_organisations() -> list[OrganisationRead]:
    """List displayable organisations.

    This endpoint is retained for backwards compatibility.
    It will always return a list of only one organisation as only one organisation
    is currently allowed.

    """
    query = """
    query OrganisationQuery {
      org {
        uuid, user_key, name
      }
    }
    """
    r = await execute_graphql(query)
    if r.errors:
        error = one(r.errors)
        if error.original_error:
            raise error.original_error
        raise ValueError(error)
    return [r.data["org"]]


class OrganisationLevelRead(OrganisationRead):
    child_count: int
    person_count: int
    unit_count: int
    engagement_count: int
    association_count: int
    leave_count: int
    role_count: int
    manager_count: int


def filter_data(data: Iterable, key: str, value: Any) -> filter:
    return filter(lambda obj: obj[key] == value, data)


@org_router.get(
    "/o/{orgid}/",
    response_model=OrganisationLevelRead,
    response_model_exclude_unset=True,
)
async def get_organisation(orgid: UUID) -> OrganisationLevelRead:
    """Obtain the initial level of an organisation."""
    query = """
    query OrganisationQuery {
      employees {
        objects { uuid }
      }
      org_units {
        objects { uuid, parent_uuid }
      }
      associations {
        objects { uuid }
      }
      engagements {
        objects { uuid }
      }
      leaves {
        objects { uuid }
      }
      roles {
        objects { uuid }
      }
      managers {
        objects { uuid }
      }
      org {
        uuid, user_key, name
      }
    }
    """
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(query)
    if response.errors:
        error = one(response.errors)
        if error.original_error:
            raise error.original_error
        raise ValueError(error)

    if response.data["org"]["uuid"] != str(orgid):
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    org_units = flatten_data(response.data["org_units"])
    child_count = ilen(filter_data(org_units, "parent_uuid", str(orgid)))
    return {
        "uuid": response.data["org"]["uuid"],
        "user_key": response.data["org"]["user_key"],
        "name": response.data["org"]["name"],
        "child_count": child_count,
        "person_count": len(response.data["employees"]),
        "unit_count": len(response.data["org_units"]),
        "engagement_count": len(response.data["engagements"]),
        "association_count": len(response.data["associations"]),
        "leave_count": len(response.data["leaves"]),
        "role_count": len(response.data["roles"]),
        "manager_count": len(response.data["managers"]),
    }


class OrganisationUnitCount(OrganisationUnitRead):
    child_count: int
    engagement_count: int = 0
    association_count: int = 0


@org_router.get(
    "/o/{parentid}/children",
    response_model=list[OrganisationUnitCount],
    response_model_exclude_unset=True,
)
async def get_org_children(
    parentid: UUID,
    at: Optional[Union[date, datetime]] = None,
    count: Optional[set[Literal["engagement", "association"]]] = Query(None),
    org_unit_hierarchy: Optional[UUID] = None,
) -> list[OrganisationUnitCount]:
    """Obtain the list of nested units within an organisation."""
    query = """
    query OrganisationChildrenQuery(
      $from_date: DateTime,
      $engagements: Boolean!,
      $associations: Boolean!,
      $hierarchy: Boolean!) {
        org_units(from_date: $from_date) {
          objects {
            name
            user_key
            uuid
            parent_uuid
            children {
              uuid
            }
            validity {
              from
              to
            }
            org_unit_hierarchy @include(if: $hierarchy)
            associations @include(if: $associations) {
              uuid
            }
            engagements @include(if: $engagements) {
              uuid
            }
          }
        }
      }
    """
    count = count or set()
    variables = {
        "engagements": "engagement" in count,
        "associations": "association" in count,
        "hierarchy": bool(org_unit_hierarchy),
    }
    variables |= {"from_date": at} if at is not None else dict()
    response = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )

    # Filter by parent uuid
    ou_data = flatten_data(response.data["org_units"])
    org_units: list[dict[str, Any]] = list(
        filter_data(ou_data, "parent_uuid", str(parentid))
    )

    if not org_units:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=str(parentid))

    # Filter by hierarchy
    if org_unit_hierarchy is not None:
        org_units = list(
            filter_data(org_units, "org_unit_hierarchy", str(org_unit_hierarchy))
        )

    for unit in org_units:
        unit |= {"child_count": len(unit.pop("children"))}
        unit |= (
            {"engagement_count": len(unit.pop("engagements", []))}
            if "engagement" in count
            else dict()
        )
        unit |= (
            {"association_count": len(unit.pop("associations", []))}
            if "association" in count
            else dict()
        )
        unit.pop("parent_uuid", "")

    return org_units
