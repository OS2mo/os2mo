# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Reading details
---------------

This section describes how to read employee and
organisational unit metadata, referred to as *details* within this
API.

For details on how to create and edit these metadata, refer to the sections on
creating and editing relations for employees and organisational units:

* http:post:`/service/details/create`
* http:post:`/service/details/edit`


"""

import collections
from datetime import date
from datetime import datetime
from functools import partial
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from more_itertools import first

from mora import util
from mora.graphapi.shim import MOAddress
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.lora import ValidityLiteral
from mora.lora import validity_tuple

from .. import common

router = APIRouter()

DetailType = collections.namedtuple(
    "DetailType",
    [
        "search",
        "scope",
    ],
)

DETAIL_TYPES = {
    "e": DetailType("tilknyttedebrugere", "bruger"),
    "ou": DetailType("tilknyttedeenheder", "organisationenhed"),
}


def filter_by_validity(validity: ValidityLiteral, element: dict):
    # This is **not** a complete filter that follows all rules of MO and Lora.
    # If validity is past and the element ends after today -> False
    # If validity is future and the element started before today -> False

    now = util.parsedatetime(util.now())

    start = element["validity"]["from"]
    end = element["validity"]["to"]

    if validity == "past":
        return end is not None and util.parsedatetime(end) < now
    if validity == "future":
        return util.parsedatetime(start) > now

    return True


@router.get(
    "/e/{eid}/details/address",
    response_model=list[MOAddress],
    response_model_exclude_unset=True,
)
async def list_addresses_employee(
    eid: UUID,
    only_primary_uuid: bool | None = None,
    at: date | datetime | None = None,
    validity: ValidityLiteral | None = None,
):
    """Fetch a list of addresses for the employee.

    Returns:
        A list of address objects akin to:

        [
           {
             "address_type": {
               "example": null,
               "name": "Email",
               "scope": "EMAIL",
               "user_key": "EmailUnit",
               "uuid": "f37f821e-2469-4fdd-bb7b-9e371df0a83b"
             },
             "href": "mailto:info@hjorring.dk",
             "name": "info@hjorring.dk",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "info@hjorring.dk",
             "uuid": "3dce271e-ba61-4a32-ad3b-9ae9b504c1bb",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "info@hjorring.dk"
           },
           {
             "address_type": {
               "example": null,
               "name": "Postadresse",
               "scope": "DAR",
               "user_key": "AddressMailUnit",
               "uuid": "ee9041d0-3a56-4935-82b3-71302e834cfe"
             },
             "href": "https://www.openstreetmap.org/\
    ?mlon=9.93195702&mlat=57.35598874&zoom=16",
             "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "uuid": "5a21cf1a-aafb-40ad-b3ac-a563f7db4881",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
           },
           {
             "address_type": {
               "example": null,
               "name": "P-nummer",
               "scope": "PNUMBER",
               "user_key": "p-nummer",
               "uuid": "8d4d0452-7e53-47d8-86c4-64262e940076"
             },
             "href": null,
             "name": "1484518640",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "1484518640",
             "uuid": "5bcc497b-22a5-4e51-bd57-63e71d3ce596",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "1484518640"
           },
           {
             "address_type": {
               "example": null,
               "name": "Returadresse",
               "scope": "DAR",
               "user_key": "AdressePostRetur",
               "uuid": "3067bcd7-53d0-474d-a9ac-3d490c738d0a"
             },
             "href": "https://www.openstreetmap.org/\
    ?mlon=9.93195702&mlat=57.35598874&zoom=16",
             "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "uuid": "a038d42a-0372-430d-bd78-f4cf65fcbc4e",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
           },
           {
             "address_type": {
               "example": null,
               "name": "Webadresse",
               "scope": "WWW",
               "user_key": "WebUnit",
               "uuid": "1ee7ee52-c597-44d7-a391-6efa7185f51c"
             },
             "href": null,
             "name": "www.hjorring.dk",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "www.hjorring.dk",
             "uuid": "a18b7b18-7e7c-472d-a7f4-3f3e734b0cba",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "www.hjorring.dk"
           },
           {
             "address_type": {
               "example": null,
               "name": "EAN-nummer",
               "scope": "EAN",
               "user_key": "EAN",
               "uuid": "e40662b4-4098-405d-909a-0a5b2ef11992"
             },
             "href": null,
             "name": "1557056556007",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "1557056556007",
             "uuid": "bc529a74-0d42-42fa-a0a4-5091d4815331",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "1557056556007"
           },
           {
             "address_type": {
               "example": null,
               "name": "Henvendelsessted",
               "scope": "DAR",
               "user_key": "AdresseHenvendelsessted",
               "uuid": "4525c0e0-0f55-4848-9222-b1b4543105a5"
             },
             "href": "https://www.openstreetmap.org/\
    ?mlon=9.93195702&mlat=57.35598874&zoom=16",
             "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "uuid": "ec3b056c-9d58-4a95-b67a-ad5dc91ce695",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
           }
        ]
    """
    if only_primary_uuid:
        query = """
            query GetAddress($uuid: UUID!, $from_date: DateTime, $to_date: DateTime) {
              employees(filter: {uuids: [$uuid], from_date: $from_date, to_date: $to_date}) {
                objects {
                  objects {
                    addresses(filter: {from_date: $from_date, to_date: $to_date}) {
                      uuid
                      user_key
                      href
                      name
                      value
                      value2
                      validity {
                        from
                        to
                      }
                      address_type_uuid
                      employee_uuid
                      engagement_uuid
                    }
                  }
                }
              }
            }
        """
    else:
        query = """
            query GetAddress($uuid: UUID!, $from_date: DateTime, $to_date: DateTime) {
              employees(filter: {uuids: [$uuid], from_date: $from_date, to_date: $to_date}) {
                objects {
                  objects {
                    addresses(filter: {from_date: $from_date, to_date: $to_date}) {
                      uuid
                      user_key
                      href
                      name
                      value
                      value2
                      validity {
                        from
                        to
                      }
                      address_type {
                        user_key
                        uuid
                        name
                        scope
                        example
                        owner
                        published
                        top_level_facet {
                          user_key
                          uuid
                          description
                        }
                        facet {
                          user_key
                          uuid
                          description
                        }
                      }
                      visibility {
                        uuid
                        name
                        user_key
                        example
                        scope
                        owner
                        published
                      }
                      employee {
                        givenname
                        surname
                        name
                        nickname
                        nickname_surname
                        nickname_givenname
                        uuid
                        seniority
                      }
                      engagement_uuid
                    }
                  }
                }
              }
            }
        """
    args = {"uuid": eid}
    if at is not None:
        args["from_date"] = at
    if validity is not None:
        start, end = validity_tuple(validity)
        args["from_date"] = start
        args["to_date"] = end
    r = await execute_graphql(
        query,
        variable_values=jsonable_encoder(args),
    )
    if r.errors:
        raise ValueError(r.errors)

    flat = flatten_data(r.data["employees"]["objects"])
    if len(flat) == 0:
        return []

    # Due to the nature of our query, the length of flat will sometimes be > 1
    # when querying historical data. However, the historical addresses reported will be
    # correct and identical for all elements, and as such we simply return the first one
    data = first(flat)["addresses"]

    for element in data:
        # the old api calls it "person" instead of "employee"
        if only_primary_uuid:
            element["person"] = {"uuid": element.pop("employee_uuid")}
            element["address_type"] = {"uuid": element.pop("address_type_uuid")}
        else:
            element["person"] = first(element.pop("employee"))

    return list(filter(partial(filter_by_validity, validity), data))


@router.get(
    "/ou/{orgid}/details/address",
    response_model=list[MOAddress],
    response_model_exclude_unset=True,
)
async def list_addresses_ou(
    orgid: UUID,
    only_primary_uuid: bool | None = None,
    at: date | datetime | None = None,
    validity: ValidityLiteral | None = None,
):
    """Fetch a list of addresses for the organisational unit.

    Returns:
        A list of address objects akin to:

        [
           {
             "address_type": {
               "example": null,
               "name": "Email",
               "scope": "EMAIL",
               "user_key": "EmailUnit",
               "uuid": "f37f821e-2469-4fdd-bb7b-9e371df0a83b"
             },
             "href": "mailto:info@hjorring.dk",
             "name": "info@hjorring.dk",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "info@hjorring.dk",
             "uuid": "3dce271e-ba61-4a32-ad3b-9ae9b504c1bb",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "info@hjorring.dk"
           },
           {
             "address_type": {
               "example": null,
               "name": "Postadresse",
               "scope": "DAR",
               "user_key": "AddressMailUnit",
               "uuid": "ee9041d0-3a56-4935-82b3-71302e834cfe"
             },
             "href": "https://www.openstreetmap.org/\
    ?mlon=9.93195702&mlat=57.35598874&zoom=16",
             "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "uuid": "5a21cf1a-aafb-40ad-b3ac-a563f7db4881",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
           },
           {
             "address_type": {
               "example": null,
               "name": "P-nummer",
               "scope": "PNUMBER",
               "user_key": "p-nummer",
               "uuid": "8d4d0452-7e53-47d8-86c4-64262e940076"
             },
             "href": null,
             "name": "1484518640",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "1484518640",
             "uuid": "5bcc497b-22a5-4e51-bd57-63e71d3ce596",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "1484518640"
           },
           {
             "address_type": {
               "example": null,
               "name": "Returadresse",
               "scope": "DAR",
               "user_key": "AdressePostRetur",
               "uuid": "3067bcd7-53d0-474d-a9ac-3d490c738d0a"
             },
             "href": "https://www.openstreetmap.org/\
    ?mlon=9.93195702&mlat=57.35598874&zoom=16",
             "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "uuid": "a038d42a-0372-430d-bd78-f4cf65fcbc4e",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
           },
           {
             "address_type": {
               "example": null,
               "name": "Webadresse",
               "scope": "WWW",
               "user_key": "WebUnit",
               "uuid": "1ee7ee52-c597-44d7-a391-6efa7185f51c"
             },
             "href": null,
             "name": "www.hjorring.dk",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "www.hjorring.dk",
             "uuid": "a18b7b18-7e7c-472d-a7f4-3f3e734b0cba",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "www.hjorring.dk"
           },
           {
             "address_type": {
               "example": null,
               "name": "EAN-nummer",
               "scope": "EAN",
               "user_key": "EAN",
               "uuid": "e40662b4-4098-405d-909a-0a5b2ef11992"
             },
             "href": null,
             "name": "1557056556007",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "1557056556007",
             "uuid": "bc529a74-0d42-42fa-a0a4-5091d4815331",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "1557056556007"
           },
           {
             "address_type": {
               "example": null,
               "name": "Henvendelsessted",
               "scope": "DAR",
               "user_key": "AdresseHenvendelsessted",
               "uuid": "4525c0e0-0f55-4848-9222-b1b4543105a5"
             },
             "href": "https://www.openstreetmap.org/\
    ?mlon=9.93195702&mlat=57.35598874&zoom=16",
             "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
             "uuid": "ec3b056c-9d58-4a95-b67a-ad5dc91ce695",
             "validity": {
               "from": "1960-01-01",
               "to": null
             },
             "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
           }
        ]
    """
    if only_primary_uuid:
        query = """
            query GetAddress($uuid: UUID!, $from_date: DateTime, $to_date: DateTime) {
              org_units(filter: {uuids: [$uuid], from_date: $from_date, to_date: $to_date}) {
                objects {
                  objects {
                    addresses(filter: {from_date: $from_date, to_date: $to_date}) {
                      uuid
                      user_key
                      href
                      name
                      value
                      value2
                      validity {
                        from
                        to
                      }
                      address_type_uuid
                      org_unit_uuid
                    }
                  }
                }
              }
            }
        """
    else:
        query = """
            query GetAddress($uuid: UUID!, $from_date: DateTime, $to_date: DateTime) {
              org_units(filter: {uuids: [$uuid], from_date: $from_date, to_date: $to_date}) {
                objects {
                  objects {
                    addresses(filter: {from_date: $from_date, to_date: $to_date}) {
                      uuid
                      user_key
                      href
                      name
                      validity {
                        from
                        to
                      }
                      value
                      value2
                      address_type {
                        facet {
                          user_key
                          uuid
                          description
                        }
                        top_level_facet {
                          user_key
                          uuid
                          description
                        }
                        uuid
                        user_key
                        name
                        scope
                        example
                        owner
                        published
                      }
                      visibility {
                        uuid
                        name
                        user_key
                        example
                        scope
                        owner
                        published
                      }
                      org_unit {
                        name
                        user_key
                        uuid
                        validity {
                          from
                          to
                        }
                      }
                    }
                  }
                }
              }
            }
        """
    args = {"uuid": orgid}
    if at is not None:
        args["from_date"] = at
    if validity is not None:
        start, end = validity_tuple(validity, now=at)

        args["from_date"] = start
        args["to_date"] = end
    r = await execute_graphql(
        query,
        variable_values=jsonable_encoder(args),
    )
    if r.errors:
        raise ValueError(r.errors)

    flat = flatten_data(r.data["org_units"]["objects"])
    if len(flat) == 0:
        return []

    # Due to the nature of our query, the length of flat will sometimes be > 1
    # when querying historical data. However, the historical addresses reported will be
    # correct and identical for all elements, and as such we simply return the first one
    data = first(flat)["addresses"]

    for element in data:
        if only_primary_uuid:
            element["address_type"] = {"uuid": element.pop("address_type_uuid")}
            element["org_unit"] = {"uuid": element.pop("org_unit_uuid")}
        else:
            element["org_unit"] = first(element["org_unit"])

    return list(filter(partial(filter_by_validity, validity), data))


async def get_detail(type, id: UUID, function):
    """Helper function for fetching details for employees and organisation units.

    Args:
        type: The type of entry to query.
            'ou' for querying a organisation units.
            'e' for querying an employees.
        id: UUID of the organisational unit or employee to fetch details for.
        function: The detail handler function name, aka. the details type to fetch.

    Returns:
        A list of detail entities.

    Note:
        All requests contain validity objects on the following form:

        {
            "from": "2016-01-01",
            "to": "2017-12-31"
        }

        Where:
        * from: Is the from or start date in ISO-8601 format
        * to: Is the to or end date in ISO-8601 format

    Query Params:
        at: Show details valid at this point in time, in ISO-8601 format.
        validity: Only show *past*, *present* or *future* values.
                  Defaults to showing *present* values.
        start: Index of first item for paging.
        limit: Maximum items.
        only_primary_uuid: If the response should only contain the UUIDs of the various
                           related persons, org units and classes, as opposed to a full
                           lookup containing the relevant names etc.
                           This can lead to increased performance in some cases.
    """
    id = str(id)
    c = common.get_connector()

    from ..handler import reading

    cls = reading.get_handler_for_type(function)
    return await cls.get_from_type(c, type, id)


@router.get("/e/{id}/details/association")
async def list_associations_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
    first_party_perspective: Any | None = None,
):
    """Fetch a list of associations for the employee.

    Returns:
        A list of association objects akin to:

        [
           {
             "association_type": {
               "example": null,
               "name": "Formand",
               "scope": "TEXT",
               "user_key": "Formand",
               "uuid": "6968bcf7-e33f-41cd-a218-28d850d5f02d"
             },
             "org_unit": {
               "name": "Borgmesterens Afdeling",
               "user_key": "Borgmesterens Afdeling",
               "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "person": {
               "name": "J\u00f8rgen Siig J\u00f8rgensen",
               "uuid": "f1458657-2498-4c53-82e0-e3857f32875b"
             },
             "primary": null,
             "user_key": "f1458657-2498-4c53-82e0-e3857f32875b \
    b6c11152-0645-4712-a207-ba2c53b391ab Tilknytning",
             "uuid": "ad366f7e-4294-4602-abd3-2bd6db20060e",
             "validity": {
               "from": "1996-04-21",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="e", id=id, function="association")


@router.get("/ou/{id}/details/association")
async def list_associations_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
    first_party_perspective: Any | None = None,
):
    """Fetch a list of associations for the organisation unit.

    Returns:
        A list of association objects akin to:

        [
           {
             "association_type": {
               "example": null,
               "name": "Formand",
               "scope": "TEXT",
               "user_key": "Formand",
               "uuid": "6968bcf7-e33f-41cd-a218-28d850d5f02d"
             },
             "org_unit": {
               "name": "Borgmesterens Afdeling",
               "user_key": "Borgmesterens Afdeling",
               "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "person": {
               "name": "J\u00f8rgen Siig J\u00f8rgensen",
               "uuid": "f1458657-2498-4c53-82e0-e3857f32875b"
             },
             "primary": null,
             "user_key": "f1458657-2498-4c53-82e0-e3857f32875b \
    b6c11152-0645-4712-a207-ba2c53b391ab Tilknytning",
             "uuid": "ad366f7e-4294-4602-abd3-2bd6db20060e",
             "validity": {
               "from": "1996-04-21",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="ou", id=id, function="association")


@router.get("/e/{id}/details/employee")
async def list_employees_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of employees for the employee.

    Returns:
        A list of employee objects akin to:

        [
           {
             "cpr_no": "0602602389",
             "givenname": "Solveig",
             "name": "Solveig Kuhlenhenke",
             "nickname": "Sol Henk",
             "nickname_givenname": "Sol",
             "nickname_surname": "Henk",
             "org": {
               "name": "Kolding Kommune",
               "user_key": "Kolding Kommune",
               "uuid": "3b866d97-0b1f-48e0-8078-686d96f430b3"
             },
             "surname": "Kuhlenhenke",
             "user_key": "SolveigK",
             "uuid": "23d2dfc7-6ceb-47cf-97ed-db6beadcb09b",
             "validity": {
               "from": "2020-08-05",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="e", id=id, function="employee")


@router.get("/ou/{id}/details/employee")
async def list_employees_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of employees for the organisation unit.

    Returns:
        A list of employee objects akin to:

        [
           {
             "cpr_no": "0602602389",
             "givenname": "Solveig",
             "name": "Solveig Kuhlenhenke",
             "nickname": "Sol Henk",
             "nickname_givenname": "Sol",
             "nickname_surname": "Henk",
             "org": {
               "name": "Kolding Kommune",
               "user_key": "Kolding Kommune",
               "uuid": "3b866d97-0b1f-48e0-8078-686d96f430b3"
             },
             "surname": "Kuhlenhenke",
             "user_key": "SolveigK",
             "uuid": "23d2dfc7-6ceb-47cf-97ed-db6beadcb09b",
             "validity": {
               "from": "2020-08-05",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="ou", id=id, function="employee")


@router.get("/e/{id}/details/engagement")
async def list_engagements_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
    calculate_primary: Any | None = None,
):
    """Fetch a list of engagements for the employee.

    Args:
        calculate_primary:
            Calculate whether the engagement is the primary engagement or not.
            If multiple engagements exist for a user we look at the engagement with the
            associated primary class with the highest _scope_.

    Returns:
        A list of engagement objects akin to:

        [
           {
             "engagement_type": {
               "example": null,
               "name": "Ansat",
               "scope": "TEXT",
               "user_key": "Ansat",
               "uuid": "60315fce-995c-4874-ad7b-48b27aaafb25"
             },
             "job_function": {
               "example": null,
               "name": "Personalekonsulent",
               "scope": "TEXT",
               "user_key": "Personalekonsulent",
               "uuid": "c5d76586-32fe-41e8-b702-27636265d696"
             },
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "person": {
               "name": "Martin F\u00e8vre Laustsen",
               "uuid": "7d5cdeec-8333-46e9-8a69-b4a2351f4d01"
             },
             "primary": {
               "name": "Primær",
               "user_key": "primaer",
               "scope": 100,
               "uuid": "b708d0e2-8b2d-47ed-98b9-6548103f5de3",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "is_primary": true,
             "fraction": 20,
             "extension_1": "value_1",
             "extension_2": "value_2",
             "extension_3": "value_3",
             "extension_4": "value_4",
             "extension_5": "value_5",
             "extension_6": "value_6",
             "extension_7": "value_7",
             "extension_8": "value_8",
             "extension_9": "value_9",
             "extension_10": "value_10",
             "user_key": "2368360a-c860-458c-9725-d678c5efbf79",
             "uuid": "6467fbb0-dd62-48ae-90be-abdef7e66aa7",
             "validity": {
               "from": "1997-04-16",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="e", id=id, function="engagement")


@router.get("/ou/{id}/details/engagement")
async def list_engagements_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
    calculate_primary: Any | None = None,
):
    """Fetch a list of engagements for the organisation unit.

    Args:
        calculate_primary:
            Calculate whether the engagement is the primary engagement or not.
            If multiple engagements exist for a user we look at the engagement with the
            associated primary class with the highest _scope_.

    Returns:
        A list of engagement objects akin to:

        [
           {
             "engagement_type": {
               "example": null,
               "name": "Ansat",
               "scope": "TEXT",
               "user_key": "Ansat",
               "uuid": "60315fce-995c-4874-ad7b-48b27aaafb25"
             },
             "job_function": {
               "example": null,
               "name": "Personalekonsulent",
               "scope": "TEXT",
               "user_key": "Personalekonsulent",
               "uuid": "c5d76586-32fe-41e8-b702-27636265d696"
             },
             "org_unit": {
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "person": {
               "name": "Martin F\u00e8vre Laustsen",
               "uuid": "7d5cdeec-8333-46e9-8a69-b4a2351f4d01"
             },
             "primary": {
               "name": "Primær",
               "user_key": "primaer",
               "scope": 100,
               "uuid": "b708d0e2-8b2d-47ed-98b9-6548103f5de3",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "is_primary": true,
             "fraction": 20,
             "extension_1": "value_1",
             "extension_2": "value_2",
             "extension_3": "value_3",
             "extension_4": "value_4",
             "extension_5": "value_5",
             "extension_6": "value_6",
             "extension_7": "value_7",
             "extension_8": "value_8",
             "extension_9": "value_9",
             "extension_10": "value_10",
             "user_key": "2368360a-c860-458c-9725-d678c5efbf79",
             "uuid": "6467fbb0-dd62-48ae-90be-abdef7e66aa7",
             "validity": {
               "from": "1997-04-16",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="ou", id=id, function="engagement")


@router.get("/e/{id}/details/it")
async def list_its_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of its for the employee.

    Returns:
        A list of ituser objects akin to:

        [
           {
             "itsystem": {
               "name": "Active Directory",
               "reference": null,
               "system_type": null,
               "user_key": "Active Directory",
               "uuid": "ef1acc94-dc2f-49e3-aa03-73a02262393c",
               "validity": {
                 "from": "1900-01-01",
                 "to": null
               }
             },
             "org_unit": null,
             "person": {
               "name": "Bente Pedersen",
               "uuid": "c9eaffad-971e-4c0c-8516-44c5d29ca092"
             },
             "user_key": "BenteP",
             "uuid": "9045b3e3-5cb9-416d-9499-87c6648695d4",
             "validity": {
               "from": "1978-12-22",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="e", id=id, function="it")


@router.get("/ou/{id}/details/it")
async def list_its_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of its for the organisation unit.

    Returns:
        A list of ituser objects akin to:

        [
           {
             "itsystem": {
               "name": "Active Directory",
               "reference": null,
               "system_type": null,
               "user_key": "Active Directory",
               "uuid": "ef1acc94-dc2f-49e3-aa03-73a02262393c",
               "validity": {
                 "from": "1900-01-01",
                 "to": null
               }
             },
             "org_unit": null,
             "person": {
               "name": "Bente Pedersen",
               "uuid": "c9eaffad-971e-4c0c-8516-44c5d29ca092"
             },
             "user_key": "BenteP",
             "uuid": "9045b3e3-5cb9-416d-9499-87c6648695d4",
             "validity": {
               "from": "1978-12-22",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="ou", id=id, function="it")


@router.get("/e/{id}/details/kle")
async def list_kles_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of kles for the employee."""
    return await get_detail(type="e", id=id, function="kle")


@router.get("/ou/{id}/details/kle")
async def list_kles_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of kles for the organisation unit."""
    return await get_detail(type="ou", id=id, function="kle")


@router.get("/e/{id}/details/leave")
async def list_leaves_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of leaves for the employee."""
    return await get_detail(type="e", id=id, function="leave")


@router.get("/ou/{id}/details/leave")
async def list_leaves_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of leaves for the organisation unit."""
    return await get_detail(type="ou", id=id, function="leave")


@router.get("/e/{id}/details/manager")
async def list_managers_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
    inherit_manager: Any | None = None,
):
    """Fetch a list of managers for the employee.

    Args:
        inherit_manager:
            Whether inheritance of managers should be performed.
            E.g. if a manager is not found for a given unit, the tree is searched
            upwards until a manager is found.

    Returns:
        A list of manager objects akin to:

        [
           {
             "address": [],
             "manager_level": {
               "example": null,
               "name": "Niveau 4",
               "scope": "TEXT",
               "user_key": "Niveau 4",
               "uuid": "049fb201-fc32-40e3-80c7-4cd7cb89a9a3"
             },
             "manager_type": {
               "example": null,
               "name": "Direkt\u00f8r",
               "scope": "TEXT",
               "user_key": "Direkt\u00f8r",
               "uuid": "d4c5983b-c4cd-43f2-b18a-653387172b08"
             },
             "org_unit": {
               "name": "Borgmesterens Afdeling",
               "user_key": "Borgmesterens Afdeling",
               "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "person": {
               "name": "Elisabeth B\u00f8gholm Meils\u00f8e",
               "uuid": "1cd7d465-e525-402f-b93e-e60a20a6e494"
             },
             "responsibility": [
               {
                 "example": null,
                 "name": "Personale: ans\u00e6ttelse/afskedigelse",
                 "scope": "TEXT",
                 "user_key": "Personale: ans\u00e6ttelse/afskedigelse",
                 "uuid": "07b8b1f5-a441-46d4-b523-c2f44a6dd538"
               },
               {
                 "example": null,
                 "name": "Ansvar for bygninger og arealer",
                 "scope": "TEXT",
                 "user_key": "Ansvar for bygninger og arealer",
                 "uuid": "76a2a5cc-3274-4110-993b-38110eaea182"
               },
               {
                 "example": null,
                 "name": "Beredskabsledelse",
                 "scope": "TEXT",
                 "user_key": "Beredskabsledelse",
                 "uuid": "c2add5de-a3a7-41e8-88e9-a71f7b75dc60"
               }
             ],
             "user_key": "d1d2cc75-b86b-45a3-8110-ac7ccbd5993a",
             "uuid": "4a3074ec-bd64-4410-b9ac-08b1e48d6701",
             "validity": {
               "from": "2010-04-08",
               "to": null
             }
           }
         ]
    """
    return await get_detail(type="e", id=id, function="manager")


@router.get("/ou/{id}/details/manager")
async def list_managers_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
    inherit_manager: Any | None = None,
):
    """Fetch a list of managers for the organisation unit.

    Args:
        inherit_manager:
            Whether inheritance of managers should be performed.
            E.g. if a manager is not found for a given unit, the tree is searched
            upwards until a manager is found.

    Returns:
        A list of manager objects akin to:

        [
           {
             "address": [],
             "manager_level": {
               "example": null,
               "name": "Niveau 4",
               "scope": "TEXT",
               "user_key": "Niveau 4",
               "uuid": "049fb201-fc32-40e3-80c7-4cd7cb89a9a3"
             },
             "manager_type": {
               "example": null,
               "name": "Direkt\u00f8r",
               "scope": "TEXT",
               "user_key": "Direkt\u00f8r",
               "uuid": "d4c5983b-c4cd-43f2-b18a-653387172b08"
             },
             "org_unit": {
               "name": "Borgmesterens Afdeling",
               "user_key": "Borgmesterens Afdeling",
               "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "person": {
               "name": "Elisabeth B\u00f8gholm Meils\u00f8e",
               "uuid": "1cd7d465-e525-402f-b93e-e60a20a6e494"
             },
             "responsibility": [
               {
                 "example": null,
                 "name": "Personale: ans\u00e6ttelse/afskedigelse",
                 "scope": "TEXT",
                 "user_key": "Personale: ans\u00e6ttelse/afskedigelse",
                 "uuid": "07b8b1f5-a441-46d4-b523-c2f44a6dd538"
               },
               {
                 "example": null,
                 "name": "Ansvar for bygninger og arealer",
                 "scope": "TEXT",
                 "user_key": "Ansvar for bygninger og arealer",
                 "uuid": "76a2a5cc-3274-4110-993b-38110eaea182"
               },
               {
                 "example": null,
                 "name": "Beredskabsledelse",
                 "scope": "TEXT",
                 "user_key": "Beredskabsledelse",
                 "uuid": "c2add5de-a3a7-41e8-88e9-a71f7b75dc60"
               }
             ],
             "user_key": "d1d2cc75-b86b-45a3-8110-ac7ccbd5993a",
             "uuid": "4a3074ec-bd64-4410-b9ac-08b1e48d6701",
             "validity": {
               "from": "2010-04-08",
               "to": null
             }
           }
         ]
    """
    return await get_detail(type="ou", id=id, function="manager")


@router.get("/e/{id}/details/org_unit")
async def list_org_units_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of org_units for the employee.

    Returns:
        A list of organisational unit objects akin to:

        [
           {
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
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "time_planning": null,
             "user_key": "Borgmesterens Afdeling",
             "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
             "validity": {
               "from": "1960-01-01",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="e", id=id, function="org_unit")


@router.get("/ou/{id}/details/org_unit")
async def list_org_units_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of org_units for the organisation unit.

    Returns:
        A list of organisational unit objects akin to:

        [
           {
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
               "name": "Hj\u00f8rring Kommune",
               "user_key": "Hj\u00f8rring Kommune",
               "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
               "validity": {
                 "from": "1960-01-01",
                 "to": null
               }
             },
             "time_planning": null,
             "user_key": "Borgmesterens Afdeling",
             "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
             "validity": {
               "from": "1960-01-01",
               "to": null
             }
           }
        ]
    """
    return await get_detail(type="ou", id=id, function="org_unit")


@router.get("/e/{id}/details/owner")
async def list_owners_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of owners for the employee."""
    return await get_detail(type="e", id=id, function="owner")


@router.get("/ou/{id}/details/owner")
async def list_owners_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of owners for the organisation unit."""
    return await get_detail(type="ou", id=id, function="owner")


@router.get("/e/{id}/details/related_unit")
async def list_related_units_employee(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of related_units for the employee."""
    return await get_detail(type="e", id=id, function="related_unit")


@router.get("/ou/{id}/details/related_unit")
async def list_related_units_ou(
    id: UUID,
    at: Any | None = None,
    validity: Any | None = None,
    only_primary_uuid: Any | None = None,
):
    """Fetch a list of related_units for the organisation unit."""
    return await get_detail(type="ou", id=id, function="related_unit")
