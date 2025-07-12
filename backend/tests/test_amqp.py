# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
import pytest
from sqlalchemy import select
from datetime import datetime
from mora.db import AMQPSubsystem
from uuid import uuid4
from mora.db import AsyncSession
from mora.amqp import _emit_events
from tests.conftest import GraphAPIPost
from typing import Any
from uuid import UUID
from collections.abc import Callable
from typing import Awaitable


@pytest.fixture
def get_last_run(empty_db: AsyncSession) -> Callable[[], Awaitable[datetime]]:
    async def inner() -> datetime:
        return await empty_db.scalar(
            select(AMQPSubsystem.last_run).where(AMQPSubsystem.id == 1)
        )

    return inner


@pytest.fixture
def emit_events(
    empty_db: AsyncSession,
    get_last_run: Callable[[], Awaitable[datetime]],
) -> Callable[[], Awaitable[list[tuple[str, UUID]]]]:

    async def inner() -> list[tuple[str, UUID]]:
        amqp_system = AsyncMock()

        start = await get_last_run()
        await _emit_events(empty_db, amqp_system)
        end = await get_last_run()
        assert start < end

        events = [
            (call.kwargs["routing_key"], UUID(call.kwargs["payload"]))
            for call in amqp_system.publish_message.await_args_list
        ]
        return events

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
) -> None:
    events = await emit_events()
    assert events == []


@pytest.mark.integration_test
async def test_emit_org_unit_event(
    emit_events: Callable[[], Awaitable[None]],
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

    events = await emit_events()
    assert events == [("org_unit", org_unit_uuid)]
