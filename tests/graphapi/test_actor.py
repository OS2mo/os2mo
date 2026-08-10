# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_read_actors(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
) -> None:
    """The actors collection exposes the actor data-source.

    The actor table is kept ajour as actors interact with OS2mo, so creating
    data registers the authenticated actor ("bruce") as a side effect.
    """
    create_person()

    query = """
        query ReadActors {
          actors {
            objects {
              uuid
              display_name
            }
          }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    display_names = {
        actor["display_name"] for actor in response.data["actors"]["objects"]
    }
    assert "bruce" in display_names


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_read_actors_uuid_filter(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
) -> None:
    """Actors can be filtered by their UUID."""
    create_person()

    query = """
        query ReadActors($filter: ActorFilter) {
          actors(filter: $filter) {
            objects {
              uuid
              display_name
            }
          }
        }
    """
    response = graphapi_post(query, {"filter": None})
    assert response.errors is None
    assert response.data
    bruce = one(
        actor
        for actor in response.data["actors"]["objects"]
        if actor["display_name"] == "bruce"
    )

    response = graphapi_post(query, {"filter": {"uuids": [bruce["uuid"]]}})
    assert response.errors is None
    assert response.data
    filtered = one(response.data["actors"]["objects"])
    assert filtered["uuid"] == bruce["uuid"]
    assert filtered["display_name"] == "bruce"
