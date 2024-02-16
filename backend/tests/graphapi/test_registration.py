# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import uuid4

import pytest
from more_itertools import one


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_writing_registration(graphapi_post) -> None:
    """Integrationtest for reading and writing registrations."""
    query = """
        query ReadObjectRegistration($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid]}) {
            objects {
              uuid
              registrations {
                registration_id
                start
                end
              }
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    # We cannot assert anything meaningful about the registration_id at this point, as
    # the ID is derived from a postgresql id sequence
    registration = one(org_unit["registrations"])
    assert registration["end"] is None

    # Update the org-unit to create a new registration
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

    # Fetch registrations now, expecting to find one more
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    # We expect exactly two registrations now
    old_registration, new_registration = org_unit["registrations"]
    # with the old registration being the same as before, but end is no longer None
    assert old_registration["registration_id"] == registration["registration_id"]
    assert old_registration["start"] == registration["start"]
    assert old_registration["end"] is not None
    # as the new registration has the None instead
    assert new_registration["end"] is None
    assert new_registration["registration_id"] > old_registration["registration_id"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_read_object_registration(graphapi_post) -> None:
    """Object registration reading integration-test."""
    query = """
        query ReadObjectRegistration($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid]}) {
            objects {
              uuid
              registrations {
                actor
                model
                uuid
                start
                end
              }
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    registration = one(org_unit["registrations"])
    assert registration["actor"] == "05211100-baad-1110-006e-6f2075756964"
    assert registration["model"] == "org_unit"
    assert registration["uuid"] == uuid
    datetime.fromisoformat(registration["start"])
    assert registration["end"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_read_top_level_registration(graphapi_post) -> None:
    """Top-level registration reading integration-test."""
    query = """
        query ReadRegistration($uuid: UUID!) {
          registrations(filter: {uuids: [$uuid]}) {
            objects {
              actor
              model
              uuid
              start
              end
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    registration = one(response.data["registrations"]["objects"])

    assert registration["actor"] == "05211100-baad-1110-006e-6f2075756964"
    assert registration["model"] == "org_unit"
    assert registration["uuid"] == uuid
    datetime.fromisoformat(registration["start"])
    assert registration["end"] is None
