# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_reading_actor(graphapi_post, set_auth) -> None:
    """Integrationtest for reading PersonActor."""
    # Set the logged in user to have a known uuid
    objectguid = uuid4()
    set_auth("admin", objectguid)
    # Create an it-account with this uuid in external id
    it = graphapi_post(
        """
            mutation MyMutation($external_id: String!) {
              ituser_create(
                input: {
                  person: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
                  validity: { from: "2020-08-01" }
                  itsystem: "0872fb72-926d-4c5c-a063-ff800b8ee697"
                  user_key: "username"
                  external_id: $external_id
                }
              ) {
                uuid
              }
            }
        """,
        variables={"external_id": str(objectguid)},
    )
    assert it.errors is None

    # Note: we might actually just test the actor on this it-user. But for illustration purposes we make a registration on an org_unit
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    response = graphapi_post(
        """
            mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) {
                    uuid
                }
            }
        """,
        {
            "input": {
                "uuid": uuid,
                "validity": {"from": "2050-01-01"},
                "name": str(uuid4()),
            }
        },
    )
    assert response.errors is None
    assert response.data == {"org_unit_update": {"uuid": uuid}}

    # Fetch registrations and the person who made the registrations
    response = graphapi_post(
        """
        query ReadObjectRegistration($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid]}) {
            objects {
              uuid
              registrations {
              actor
              actor_object {
                ... on PersonActor {
                  person {
                    current {
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    """,
        {"uuid": uuid},
    )
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    # We expect exactly two registrations now
    old_registration, new_registration = org_unit["registrations"]
    # The first is not made by a person
    assert old_registration["actor_object"] == {}
    # The other is created by Anders And
    assert UUID(new_registration["actor"]) == objectguid
    assert new_registration["actor_object"]["person"]["current"]["name"] == "Anders And"
