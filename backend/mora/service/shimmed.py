# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID
from fastapi import APIRouter

from more_itertools import one

from mora.service.employee import router
from ..graphapi.shim import execute_graphql
from .. import exceptions


@router.get("/e/{id}/")
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
            uuid
          }
        }
        """

        def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
            return one(r.data["employees"])

    else:
        query = """
        query EmployeeQuery($uuid: UUID!) {
          employees(uuids: [$uuid]) {
            uuid, user_key, cpr_no
            givenname, surname
            nickname_givenname, nickname_surname
            seniority
          }
          org {
            uuid, user_key, name
          }
        }
        """

        def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
            employee = one(r.data["employees"])
            return {
                **employee,
                "name": " ".join([employee["givenname"], employee["surname"]]).strip(),
                "nickname": " ".join(
                    [employee["nickname_givenname"], employee["nickname_surname"]]
                ).strip(),
                "org": r.data["org"],
            }

    # Execute GraphQL query to fetch required data
    r = await execute_graphql(
        query,
        variable_values={"uuid": str(id)},
    )
    if r.errors:
        raise ValueError(r.errors)
    if not r.data["employees"]:
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
            lora_version {
              major
              minor
              patch
            }
            mo_version {
              major
              minor
              patch
            }
          }
        }
        """

        # Execute GraphQL query to fetch required data
        r = await execute_graphql(query)
        if r.errors:
            raise ValueError(r.errors)

        version = r.data["version"]

        mo_version = ""
        if version["mo_version"] is not None:
            mo_version = ".".join(map(str, version["mo_version"].values()))

        commit_sha = "" if version["mo_hash"] is None else version["mo_hash"]

        lora_version = ""
        if version["lora_version"] is not None:
            lora_version = ".".join(map(str, version["lora_version"].values()))

        return {
            "mo_version": mo_version + "@" + commit_sha,
            "lora_version": lora_version,
        }

    @router.get("/service/{rest_of_path:path}")
    def no_such_endpoint(rest_of_path):
        """Throw an error on unknown `/service/` endpoints."""
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    return router
