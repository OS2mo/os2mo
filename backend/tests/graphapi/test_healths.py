# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pytest import MonkeyPatch

from mora.graphapi.versions.latest.schema import Health


def test_health_pagination(graphapi_post):
    """Test that the v3 API returns a paginated list of `Health`s."""
    health1 = Health(identifier="health1")  # type: ignore[call-arg]
    health2 = Health(identifier="health2")  # type: ignore[call-arg]
    health3 = Health(identifier="health3")  # type: ignore[call-arg]
    health4 = Health(identifier="health4")  # type: ignore[call-arg]
    health5 = Health(identifier="health5")  # type: ignore[call-arg]
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
                healths(limit: 2, cursor: "111111:eyJvZmZzZXQiOiAyLCAicmVnaXN0cmF0aW9uX3RpbWUiOiAiMjAyMy0wOS0xNFQxNjowODo1Ni4zMzg1MDgrMDI6MDAifQ==") {
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
    assert (
        healths["page_info"]["next_cursor"]
        == "eb9c34:eyJvZmZzZXQiOiA0LCAicmVnaXN0cmF0aW9uX3RpbWUiOiAiMjAyMy0wOS0xNFQxNjowODo1Ni4zMzg1MDgrMDI6MDAifQ=="
    )
