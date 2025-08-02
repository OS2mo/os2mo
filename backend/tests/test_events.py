# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import get_args
from typing import Any
from collections.abc import Awaitable
from unittest.mock import AsyncMock
from uuid import UUID
from sqlalchemy import delete
from uuid import uuid4


import pytest
from mora.db import Event
from mora.amqp import MO_TYPE, _emit_events_for_interval, _emit_events
from mora.db import AMQPSubsystem
from mora.db import AsyncSession
from sqlalchemy import select

from tests.conftest import GraphAPIPost


@pytest.fixture
def get_last_run(empty_db: AsyncSession) -> Callable[[], Awaitable[datetime]]:
    async def inner() -> datetime:
        return await empty_db.scalar(
            select(AMQPSubsystem.last_run).where(AMQPSubsystem.id == 1)
        )

    return inner


@pytest.fixture
def emit_events_with_interval(
    empty_db: AsyncSession,
) -> Callable[[datetime, datetime], Awaitable[None]]:
    async def inner(start: datetime, end: datetime) -> None:
        amqp_system = AsyncMock()

        await _emit_events_for_interval(empty_db, amqp_system, start, end)

    return inner


@pytest.fixture
def emit_events(
    empty_db: AsyncSession,
) -> Callable[[], Awaitable[None]]:
    async def inner() -> None:
        amqp_system = AsyncMock()

        await _emit_events(empty_db, amqp_system)

    return inner


@pytest.fixture
def create_mo_listener(
    root_org: UUID,
    graphapi_post: GraphAPIPost,
) -> Callable[[str], UUID]:
    def inner(routing_key: str) -> UUID:
        listener = graphapi_post(
            """
            mutation DeclareListener($namespace: String!, $user_key: String!, $routing_key: String!) {
              event_listener_declare(
                input: {namespace: $namespace, user_key: $user_key, routing_key: $routing_key}
              ) {
                uuid
              }
            }
            """,
            variables={
                "namespace": "mo",
                "user_key": routing_key,
                "routing_key": routing_key,
            },
        )
        assert listener.errors is None
        assert listener.data is not None
        return UUID(listener.data["event_listener_declare"]["uuid"])

    return inner


@pytest.fixture
def add_all_mo_listeners(
    create_mo_listener: Callable[[str], UUID]
) -> None:
    for routing_key in get_args(MO_TYPE):
        create_mo_listener(routing_key)


@pytest.fixture
def fetch_mo_events(
    graphapi_post: GraphAPIPost,
) -> Callable[[str], set[UUID]]:
    def inner(routing_key: str) -> set[UUID]:
        events = graphapi_post(
            """
            query FetchEvents($filter: FullEventFilter!) {
              events(filter: $filter) {
                objects {
                  subject
                }
              }
            }
            """,
            variables={
                "filter": {"listeners": {"routing_keys": [routing_key]}}
            },
        )
        assert events.errors is None
        assert events.data is not None
        return {UUID(event["subject"]) for event in events.data["events"]["objects"]}

    return inner


@pytest.fixture
def fetch_all_mo_events(
    add_all_mo_listeners: None,
    fetch_mo_events: Callable[[str], set[UUID]]
) -> Callable[[], dict[MO_TYPE, set[UUID]]]:
    def inner() -> dict[MO_TYPE, set[UUID]]:
        result = {
            routing_key: fetch_mo_events(routing_key)
            for routing_key in get_args(MO_TYPE)
        }
        return {key: value for key, value in result.items() if value}

    return inner


@pytest.fixture
def clear_events(
    empty_db: AsyncSession,
) -> Callable[[], Awaitable[None]]:
    async def inner() -> None:
        await empty_db.execute(delete(Event))

    return inner


@pytest.fixture
def create_org_unit(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_create"]["uuid"])

    return inner


@pytest.mark.integration_test
async def test_emit_no_data(
    emit_events: Callable[[], Awaitable[None]],
    fetch_all_mo_events: Callable[[], dict[MO_TYPE, set[UUID]]],
) -> None:
    assert fetch_all_mo_events() == {}

    await emit_events()
    assert fetch_all_mo_events() == {}


@pytest.mark.integration_test
async def test_emit_org_unit_event(
    emit_events: Callable[[], Awaitable[None]],
    fetch_all_mo_events: Callable[[], dict[MO_TYPE, set[UUID]]],
    create_org_unit: Callable[[dict[str, Any]], UUID],
) -> None:
    org_unit_uuid = create_org_unit(
        {
            "name": "Magenta ApS",
            "user_key": "maps",
            "parent": None,
            "validity": {"from": "1970-01-01T00:00:00Z"},
            "org_unit_type": str(uuid4()),
        }
    )

    await emit_events()
    assert fetch_all_mo_events() == {
        "org_unit": {org_unit_uuid}
    }
