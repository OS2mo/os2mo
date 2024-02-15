# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one


# This test is xfailed since searching does not work in our test setup.
# The issue arises from how we setup our test database, and handle test connections.
#
# The test can be reenabled once we got the LoRa database connection under control.
#
# For more details, see: test_registrations.py
@pytest.mark.xfail
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_search(graphapi_post) -> None:
    """Integrationtest for searching in GraphQL."""
    query = """
        query SearchOrgUnits($query: String!) {
          org_units(filter: {query: $query}) {
            objects {
              current {
                name
                uuid
              }
            }
          }
        }
    """
    # Fetch the current registrations
    response = graphapi_post(query, {"query": "Humanistisk"})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["name"] == "Humanistisk fakultet"
