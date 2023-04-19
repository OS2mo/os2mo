# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import uuid4

import pytest
from more_itertools import one

from tests.conftest import GQLResponse


# This test is xfailed since reading registrations does not work in our test setup.
# The issue arises from how we setup our test database, and handle test connections.
#
# During integration-test a new database is created and migrated, upon which all current
# database connections are forcefully closed, such that new connections are recreated on
# their next use.
# This forceful termination of database connections does not play nicely with SQLAlchemy
# which manage the database connections used by the MO db module.
#
# Additionally we cannot use load_fixture_data_with_reset here as LoRa changes are made
# within an uncommitted transaction and thus invisible to the database connection used
# by the MO db module.
#
# If the test is run as-is the result is that no new registrations are found after the
# edit, even if the other data changes occur. This is because all non-registration
# fields are read within the same database transaction used on the LoRa connection, but
# not on the MO db module connection.
#
# An attempt was made to create an SQLAlchemy sessionmaker, which would utilize the LoRa
# database connection as its underlying wrapped database connection. This works to some
# extend, but breaks as soon as the connection is forcefully closed, and also breaks
# invariants within SQLAlchemy as SQLAlchemy does not work with a singleton pattern for
# database connections, but rather instance them on the fly according to demand, such
# that it can optimize the database performance.
# Additionally using the LoRa database connection forces a synchronous database access,
# which does not play well with the asynchronous nature of the GraphQL resolvers. This
# could potentially be worked around using an sync-to-async executor pattern.
#
# TL;DR: The test does not work because of the immense amounts of shenanigans we pull
#        off when creating test databases and connections, but the code works outside
#        of tests.
#
# The test can be reenabled once we got the LoRa database connection under control.
@pytest.mark.xfail
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_read_registration(graphapi_post) -> None:
    """Integrationtest for reading registrations."""
    query = """
        query ReadRegistration($uuid: UUID!) {
          org_units(uuids: [$uuid]) {
            uuid
            registrations {
              registration_id
              start
              end
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response: GQLResponse = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"])
    assert org_unit["uuid"] == uuid

    # We cannot assert anything meaningful about the registration_id at this point, as
    # the ID is derived from a postgresql id sequence
    registration = one(org_unit["registrations"])
    assert registration["end"] is None

    # Update the org-unit to create a new registration
    response: GQLResponse = graphapi_post(
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
    response: GQLResponse = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"])
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
