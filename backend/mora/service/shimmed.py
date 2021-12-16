# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID

from more_itertools import one

from mora.service.employee import router as employee_router
from mora.service.orgunit import router as orgunit_router
from ..graphapi.shim import execute_graphql
from .. import exceptions


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


@orgunit_router.get("/ou/{unitid}/")
async def get_orgunit(
    unitid: UUID, only_primary_uuid: Optional[bool] = None, count: Optional[dict] = None
) -> Dict[str, Any]:
    """Get an organisational unit

    .. :quickref: Unit; Get

    :param uuid unitid: UUID of the unit to retrieve.

    :query at: the 'at date' to use, e.g. '2020-01-28'. *Optional*.
               The tree returned will only include organisational units that
               were active at the specified 'at date'.
    :query count: the name(s) of related objects to count for each unit.
                  *Optional*. If `count=association`, each organisational unit
                  in the tree is annotated with an additional
                  `association_count` key which contains the number of
                  associations in the unit. `count=engagement` is also allowed.
                  It is allowed to pass more than one `count` query parameter.

    :>json string name: The name of the org unit
    :>json string user_key: A unique key for the org unit.
    :>json uuid uuid: The UUId of the org unit
    :>json uuid parent: The parent org unit or organisation
    :>json uuid org: The organisation the unit belongs to
    :>json uuid org_unit_type: The type of org unit
    :>json uuid parent: The parent org unit or organisation
    :>json uuid time_planning: A class identifying the time planning strategy.
    :>json object validity: The validity of the created object.

    :status 200: Whenever the object exists.
    :status 404: Otherwise.

    **Example Response**:

    .. sourcecode:: json

     {
       "location": "Hj\u00f8rring Kommune",
       "name": "Borgmesterens Afdeling",
       "org": {
         "name": "Hj\u00f8rring Kommune",
         "user_key": "Hj\u00f8rring Kommune",
         "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
       },
       "org_unit_type": {
         "example": null,
         "name": "Afdeling",
         "scope": "TEXT",
         "user_key": "Afdeling",
         "uuid": "c8002c56-8226-4a72-aefa-a01dcc839391"
       },
       "parent": {
         "location": "",
         "name": "Hj\u00f8rring Kommune",
         "org": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
         },
         "org_unit_type": {
           "example": null,
           "name": "Afdeling",
           "scope": "TEXT",
           "user_key": "Afdeling",
           "uuid": "c8002c56-8226-4a72-aefa-a01dcc839391"
         },
         "parent": null,
         "time_planning": null,
         "user_key": "Hj\u00f8rring Kommune",
         "user_settings": {
           "orgunit": {
             "show_location": true,
             "show_roles": true,
             "show_user_key": false
           }
         },
         "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
         "validity": {
           "from": "1960-01-01",
           "to": null
         }
       },
       "time_planning": null,
       "user_key": "Borgmesterens Afdeling",
       "user_settings": {
         "orgunit": {
           "show_location": true,
           "show_roles": true,
           "show_user_key": false
         }
       },
       "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
       "validity": {
         "from": "1960-01-01",
         "to": null
       }
     }
    """
    from ..handler.reading import get_handler_for_type
    from mora.service.orgunit import _get_count_related
    from mora.service.orgunit import get_one_orgunit
    from mora.service.orgunit import UnitDetails
    from mora import mapping
    from .. import common

    unitid = str(unitid)

    if only_primary_uuid:
        return {mapping.UUID: unitid}

    c = common.get_connector()
    count_related = {t: get_handler_for_type(t) for t in _get_count_related()}

    query = """
    query OrganisationUnitQuery($uuid: UUID!) {
      org_units(uuids: [$uuid]) {
        uuid, name, user_key, validity { from, to }
      }
      org {
        uuid, user_key, name
      }
    }
    """
    query_result = await execute_graphql(
        query,
        variable_values={"uuid": str(unitid)},
    )
    print(query_result)

    query_result = query_result.data

    from datetime import datetime

    r = {
        "name": query_result["org_units"][0]["name"],
        "user_key": query_result["org_units"][0]["user_key"],
        "uuid": query_result["org_units"][0]["uuid"],
        "location": "",
        "user_settings": {},
        "parent": None,
        "org": {
            "name": query_result["org"]["name"],
            "user_key": query_result["org"]["user_key"],
            "uuid": query_result["org"]["uuid"],
        },
        "org_unit_type": {},
        "time_planning": {},
        "org_unit_level": {},
        "validity": {
            "from": datetime.fromisoformat(query_result["org_units"][0]["validity"]["from"]).date().isoformat(),
            "to": datetime.fromisoformat(query_result["org_units"][0]["validity"]["to"]).date().isoformat() if query_result["org_units"][0]["validity"]["to"] else None,
        },
    }

    count_related = count_related or {}
    for key, reader in count_related.items():
        r["%s_count" % key] = await reader.get_count(c, "ou", unitid)

    if not r:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=unitid)
    return r
