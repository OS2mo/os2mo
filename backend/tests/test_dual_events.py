# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import secrets
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.mo import PayloadUUID
from mora.config import get_settings
from more_itertools import one

from tests.conftest import GraphAPIPost

from .test_events import declare_listener
from .test_events import fetch_event


@pytest.fixture
def refresh_person(
    graphapi_post: GraphAPIPost,
) -> Callable[..., Any]:
    def inner(
        person_uuid: UUID,
        exchange: str | None = None,
        listener: UUID | None = None,
    ) -> Any:
        query = """
            mutation RefreshPerson($uuid: UUID!, $exchange: String, $listener: UUID) {
              employee_refresh(
                filter: {uuids: [$uuid]},
                exchange: $exchange,
                listener: $listener
              ) {
                objects
              }
            }
        """
        variables = {
            "uuid": str(person_uuid),
            "exchange": exchange,
            "listener": str(listener) if listener else None,
        }
        return graphapi_post(query, variables=variables)

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_refresh_exclusivity_error(
    refresh_person: Callable[..., Any],
) -> None:
    """Verify that using both exchange and listener/owner raises an error."""
    # Randomly generated UUIDs for greppability
    person_uuid = UUID("2d61f873-acff-4d74-a5cd-11adf5f03c7b")
    listener_uuid = UUID("0636d0f4-644d-4603-b39a-703ce8f81d33")

    response = refresh_person(
        person_uuid, exchange="some-exchange", listener=listener_uuid
    )

    error = one(response.errors)
    assert "listener/owner and exchange are mutually exclusive" in error["message"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "use_exchange, use_listener, expect_amqp, expect_graphql",
    [
        # No exchange nor listener filter -> both AMQP and GraphQL gets the event
        (False, False, True, True),
        # Exchange filter -> only AMQP system gets the event
        (True, False, True, False),
        # Listener filter -> only GraphQL gets the event
        (False, True, False, True),
    ],
)
async def test_refresh_routing(
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    refresh_person: Callable[..., Any],
    admin_client: TestClient,
    use_exchange: bool,
    use_listener: bool,
    expect_amqp: bool,
    expect_graphql: bool,
) -> None:
    """Verify routing logic based on exchange/listener parameters."""
    # Setup Person
    # Randomly generated UUIDs for greppability
    person_uuid = UUID("57656911-3d7f-4402-835a-94a28246a489")
    create_person({"uuid": str(person_uuid), "given_name": "Test", "surname": "User"})
    # Forcefully emit events to ensure no 'create' events will be emitted mid testing
    admin_client.post("/testing/amqp/emit")

    # Setup AMQPSystem and listener
    amqp_system = AMQPSystem(
        get_settings().amqp.copy(update=dict(queue_prefix=secrets.token_hex()))
    )
    amqp_uuids = set()

    @amqp_system.router.register("person")
    async def legacy_callback(uuid: PayloadUUID) -> None:
        amqp_uuids.add(uuid)

    await amqp_system.start()

    async def fetch_amqp() -> set[UUID]:
        # Sleep to ensure that the AMQPSystem has time to pickup and process the vent
        await asyncio.sleep(1)
        return set(amqp_uuids)

    # Setup GraphQL Listener
    listener_uuid = declare_listener(graphapi_post, "mo", "GraphQL_listener", "person")

    async def fetch_graphql() -> set[UUID]:
        graphql_uuids = set()
        while True:
            event = fetch_event(graphapi_post, listener_uuid)
            if event is None:
                return graphql_uuids
            graphql_uuids.add(UUID(event["subject"]))

    # Assert that no events are in either system
    # AMQP
    amqp_result = await fetch_amqp()
    assert amqp_result == set()
    # GraphQL
    graphql_result = await fetch_graphql()
    assert graphql_result == set()

    # Fire out refresh mutator
    refresh_person(
        person_uuid,
        exchange="os2mo" if use_exchange else None,
        listener=listener_uuid if use_listener else None,
    )

    # Assert that the expected events are found
    # AMQP
    amqp_result = await fetch_amqp()
    assert amqp_result == ({person_uuid} if expect_amqp else set())
    # GraphQL
    graphql_result = await fetch_graphql()
    assert graphql_result == ({person_uuid} if expect_graphql else set())
