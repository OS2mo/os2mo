# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from mora.mapping import ADMIN
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


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
              username
            }
          }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    usernames = {actor["username"] for actor in response.data["actors"]["objects"]}
    assert "bruce" in usernames


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
              username
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
        if actor["username"] == "bruce"
    )

    response = graphapi_post(query, {"filter": {"uuids": [bruce["uuid"]]}})
    assert response.errors is None
    assert response.data
    filtered = one(response.data["actors"]["objects"])
    assert filtered["uuid"] == bruce["uuid"]
    assert filtered["username"] == "bruce"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_actors_are_identified_by_username(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
) -> None:
    """The UUID in the token may change, but the actor stays the same.

    A new username, e.g. a recreated Keycloak user, is a new actor.
    """
    username = "alice@example.com"
    query = "query { me { actor { uuid username } } }"

    set_auth(ADMIN, uuid4(), preferred_username=username)
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    actor = response.data["me"]["actor"]
    assert actor["username"] == username

    set_auth(ADMIN, uuid4(), preferred_username=username)
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    assert response.data["me"]["actor"] == actor

    set_auth(ADMIN, uuid4(), preferred_username=f"new-{username}")
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    assert response.data["me"]["actor"]["uuid"] != actor["uuid"]


@pytest.mark.integration_test
@pytest.mark.envvar({"ACCESS_LOG_ENABLE": "True"})
@pytest.mark.usefixtures("empty_db")
async def test_actor_id_is_recorded_as_author(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
) -> None:
    """Changes are attributed to the actor, not the token's UUID."""
    token_uuid = uuid4()
    username = f"author-{token_uuid}"
    set_auth(ADMIN, token_uuid, preferred_username=username)

    response = graphapi_post("query { me { actor { uuid username } } }")
    assert response.errors is None
    assert response.data
    actor = response.data["me"]["actor"]
    assert actor["username"] == username
    assert actor["uuid"] != str(token_uuid)

    person = create_person()

    response = graphapi_post(
        """
        query ReadAccessLog($uuid: UUID!) {
          access_log(filter: {uuids: [$uuid]}) {
            objects { actor }
          }
        }
        """,
        {"uuid": str(person)},
    )
    assert response.errors is None
    assert response.data
    access_log = response.data["access_log"]["objects"]
    assert access_log
    assert {entry["actor"] for entry in access_log} == {actor["uuid"]}

    response = graphapi_post(
        """
        query ReadAuthor($uuid: UUID!) {
          registrations(filter: {uuids: [$uuid]}) {
            objects { actor }
          }
        }
        """,
        {"uuid": str(person)},
    )
    assert response.errors is None
    assert response.data
    registration = one(response.data["registrations"]["objects"])
    assert registration["actor"] == actor["uuid"]
