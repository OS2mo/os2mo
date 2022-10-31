# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pytest import MonkeyPatch

from mora.graphapi.versions.latest.models import HealthRead


def test_v2_shim_healths(graphapi_post):
    """Test that the v2 API returns a list of healths as before."""
    health1 = HealthRead(identifier="health1")
    health2 = HealthRead(identifier="health2")
    health3 = HealthRead(identifier="health3")
    test_data = {"health1": health1, "health2": health2, "health3": health3}

    with MonkeyPatch.context() as patch:
        patch.setattr("mora.graphapi.versions.latest.query.health_map", test_data)

        query = """
            query {
                healths {
                    identifier
                }
            }
        """
        response = graphapi_post(query, url="/graphql/v2")

    healths = response.data["healths"]
    healths = {v["identifier"] for v in healths}
    test_data = {v for v in test_data}

    assert set(healths) == set(test_data)
