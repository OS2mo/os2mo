# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_dates_filter(graphapi_post: GraphAPIPost) -> None:
    """Test dates filter behaviour."""
    query = """
        query GetOrgUnitEngagements {
          org_units(
            filter: {
              uuids: ["9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"],
              from_date: null,
              to_date: null,
            }
          ) {
            objects {
              objects {
                engagements(filter: {from_date: "1760-01-01", to_date: "1840-01-01"}) {
                  uuid
                }
              }
            }
          }
        }
    """

    # GraphQL versions prior to v21 automatically, implicitly, and forcefully inherited
    # filter parameters in all the following levels of the query.
    response_v20: GQLResponse = graphapi_post(query, url="/graphql/v20")
    assert response_v20.errors is None
    assert response_v20.data == {
        "org_units": {
            "objects": [
                {
                    "objects": [
                        {
                            "engagements": [
                                {"uuid": "301a906b-ef51-4d5c-9c77-386fb8410459"},
                                {"uuid": "d000591f-8705-4324-897a-075e3623f37b"},
                                {"uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"},
                            ]
                        },
                        {
                            "engagements": [
                                {"uuid": "301a906b-ef51-4d5c-9c77-386fb8410459"},
                                {"uuid": "d000591f-8705-4324-897a-075e3623f37b"},
                                {"uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"},
                            ]
                        },
                    ]
                }
            ]
        }
    }

    # After v21, date filtering is correctly applied at each level of the query, thus
    # we do not expect any engagements.
    response_v21: GQLResponse = graphapi_post(query, url="/graphql/v21")
    assert response_v21.errors is None
    assert response_v21.data == {
        "org_units": {
            "objects": [
                {
                    "objects": [
                        {"engagements": []},
                        {"engagements": []},
                    ]
                }
            ]
        }
    }
