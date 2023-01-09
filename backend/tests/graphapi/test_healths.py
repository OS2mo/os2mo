# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pytest import MonkeyPatch

from mora.graphapi.versions.latest.models import HealthRead


def test_health_pagination(graphapi_post):
    """Test that the v3 API returns a paginated list of `Health`s."""
    health1 = HealthRead(identifier="health1")
    health2 = HealthRead(identifier="health2")
    health3 = HealthRead(identifier="health3")
    health4 = HealthRead(identifier="health4")
    health5 = HealthRead(identifier="health5")
    test_data = {
        "health1": health1,
        "health2": health2,
        "health3": health3,
        "health4": health4,
        "health5": health5,
    }

    with MonkeyPatch.context() as patch:
        patch.setattr("mora.graphapi.versions.latest.query.health_map", test_data)
        query = """
            query {
                healths(limit: 2, cursor: "Mg==") {
                    objects {
                        status
                        identifier
                    }
                    page_info {
                        next_cursor
                    }
                }
            }
        """
        response = graphapi_post(query, url="/graphql/v3")

    healths = response.data["healths"]

    health_list = {v["identifier"] for v in healths["objects"]}
    test_data = {v for v in test_data}

    assert len(health_list) == 2
    assert all(health in test_data for health in health_list)
    assert healths["page_info"]["next_cursor"] == "NA=="
