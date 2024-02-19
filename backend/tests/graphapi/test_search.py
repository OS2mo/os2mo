# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one


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
    assert org_unit["current"]["name"] == "Humanistisk fakultet"
