# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from more_itertools import flatten
from more_itertools import one

from .. import exceptions
from ..graphapi.shim import execute_graphql
from mora.service.employee import router as employee_router
from mora.service.itsystem import router as it_router


def flatten_data(resp_dict: dict[str, Any]):
    return list(flatten([d["objects"] for d in resp_dict]))


@employee_router.get("/e/{id}/")
async def get_employee(id: UUID, only_primary_uuid: Optional[bool] = None):
    """Retrieve an employee.

    .. :quickref: Employee; Get

    :queryparam date at: Show the employee at this point in time,
        in ISO-8601 format.

    :<json string name: Full name of the employee (concatenation
        of givenname and surname).
    :<json string givenname: Given name of the employee.
    :<json string surname: Surname of the employee.
    :<json string nickname: Nickname of the employee (concatenation
        of the nickname givenname and surname).
    :<json string nickname_givenname: The given name part of the nickname.
    :<json string nickname_surname: The surname part of the nickname.
    :>json string uuid: Machine-friendly UUID.
    :>json object org: The organisation that this employee belongs to, as
        yielded by http:get:`/service/o/`.
    :>json string cpr_no: CPR number of for the corresponding person.
        Please note that this is the only means for obtaining the CPR
        number; due to confidentiality requirements, all other end
        points omit it.

    :status 200: Whenever the user ID is valid and corresponds to an
        existing user.
    :status 404: Otherwise.

    **Example Response**:

    .. sourcecode:: json

     {
       "cpr_no": "0708522600",
       "name": "Bente Pedersen",
       "givenname": "Bente",
       "surname": "Pedersen",
       "nickname": "Kjukke Mimergolf",
       "nickname_givenname": "Kjukke",
       "nickname_surname": "Mimergolf",
       "org": {
         "name": "Hj\u00f8rring Kommune",
         "user_key": "Hj\u00f8rring Kommune",
         "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
       },
       "user_key": "2ba3feb8-9617-43c1-8502-e55a2b283c58",
       "uuid": "c9eaffad-971e-4c0c-8516-44c5d29ca092"
     }

    """
    if only_primary_uuid:
        query = """
        query EmployeeQuery($uuid: UUID!) {
          employees(uuids: [$uuid]) {
            objects { uuid }
          }
        }
        """

        def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
            employees = flatten_data(r.data["employees"])
            employee = one(employees)
            return employee

    else:
        query = """
        query EmployeeQuery($uuid: UUID!) {
          employees(uuids: [$uuid]) {
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

        def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
            employees = flatten_data(r.data["employees"])
            employee = one(employees)
            return {
                **employee,
                "org": r.data["org"],
            }

    # Execute GraphQL query to fetch required data
    r = await execute_graphql(
        query,
        variable_values={"uuid": str(id)},
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
