# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

QUERY = """
query ReadObjectRegistration($uuid: UUID!) {
  org_units(filter: { uuids: [$uuid] }) {
    objects {
      uuid
      registrations {
        actor
        actor_object {
          ... on UserActor {
            it_user {
              current {
                user_key
                person {
                  name
                  uuid
                }
              }
            }
            person {
              current {
                name
                uuid
              }
            }
          }
        }
      }
    }
  }
}
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_reading_actor_from_ituser(graphapi_post, set_auth) -> None:
    """Integrationtest for reading UserActor."""
    # Set the logged in user to have a known uuid
    objectguid = uuid4()
    set_auth("admin", objectguid)
    # Create an it-account with this uuid in external id
    anders_and = UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")
    it = graphapi_post(
        """
            mutation MyMutation($external_id: String!, $person_uuid: UUID!) {
              ituser_create(
                input: {
                  person: $person_uuid
                  validity: { from: "2020-08-01" }
                  itsystem: "0872fb72-926d-4c5c-a063-ff800b8ee697"
                  user_key: "AA"
                  external_id: $external_id
                }
              ) {
                uuid
              }
            }
        """,
        variables={"external_id": str(objectguid), "person_uuid": anders_and},
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
        QUERY,
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
    assert old_registration["actor"] == "5ec0fa11-baad-1110-006d-696477617265"
    # The other is created by Anders And
    assert UUID(new_registration["actor"]) == objectguid
    assert new_registration["actor_object"]["it_user"]["current"]["user_key"] == "AA"
    actor_it_user_person = one(
        new_registration["actor_object"]["it_user"]["current"]["person"]
    )
    assert UUID(actor_it_user_person["uuid"]) == anders_and
    assert actor_it_user_person["name"] == "Anders And"
    actor_person = one(new_registration["actor_object"]["person"]["current"])
    assert UUID(actor_person["uuid"]) == anders_and
    assert actor_person["name"] == "Anders And"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_reading_actor_person(graphapi_post, set_auth) -> None:
    """Integrationtest for reading UserActor."""
    # Set the logged in user to have a known uuid
    anders_and = UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")
    set_auth("admin", anders_and)

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
        QUERY,
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
    assert old_registration["actor"] == "5ec0fa11-baad-1110-006d-696477617265"
    # The other is created by Anders And
    assert UUID(new_registration["actor"]) == anders_and
    assert new_registration["actor_object"]["it_user"]["current"]["user_key"] == "AA"
    actor_person = one(new_registration["actor_object"]["person"]["current"])
    assert UUID(actor_person["uuid"]) == anders_and
    assert actor_person["name"] == "Anders And"
