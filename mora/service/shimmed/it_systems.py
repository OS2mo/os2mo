# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from mora.graphapi.shim import execute_graphql
from mora.service.itsystem import router as it_router

from .errors import handle_gql_error


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
        objects {
          current {
            uuid, name, system_type, user_key
          }
        }
      }
      org {
        uuid
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)
    if response.data["org"]["uuid"] != orgid:
        return []
    return [x["current"] for x in response.data["itsystems"]["objects"]]
