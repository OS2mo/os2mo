# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Make sure events are generated for all registrations.

Regression test for #69713.
"""

from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy import text

from mora import amqp
from mora.amqp import DummyAMQPSystem
from tests.conftest import AnotherTransaction


class AMQPSystemMock(DummyAMQPSystem):
    def __init__(self) -> None:
        self.published: list[UUID] = []

    async def publish_message(self, routing_key, payload, exchange=None) -> None:
        self.published.append(UUID(payload))


async def _run_event_generator(another_transaction: AnotherTransaction) -> list[UUID]:
    recorder = AMQPSystemMock()
    async with another_transaction() as (_, session):
        await amqp._emit_events(session, recorder)
    return recorder.published


async def _write_object(session: Any, uuid: UUID) -> None:
    await session.execute(text("insert into bruger (id) values (:id)"), {"id": uuid})
    await session.execute(
        text(
            """
            insert into bruger_registrering (bruger_id, registrering) values
            (:id, row(tstzrange(now(), null), 'Opstaaet'::livscykluskode,
             :actor, 'test')::registreringbase)
            """
        ),
        {"id": uuid, "actor": uuid4()},
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_registration_emitted_when_writer_outlives_publisher_run(
    another_transaction: AnotherTransaction,
) -> None:
    tx1_uuid = UUID("b0c0ffee-0000-4000-8000-000000000001")
    tx2_uuid = UUID("b0c0ffee-0000-4000-8000-000000000002")

    async with another_transaction() as (_, tx1):
        # tx1 writes (pinning `now` before tx2 `now`), but does not commit yet.
        await _write_object(tx1, tx1_uuid)

        async with another_transaction() as (_, tx2):
            await _write_object(tx2, tx2_uuid)

        # tx1 still uncommited!
        assert await _run_event_generator(another_transaction) == [tx2_uuid]

    # tx1 is visible now, and we must emit an event for it, even though its
    # timestamp predates tx2 which was emitted in the other event gen run.
    assert await _run_event_generator(another_transaction) == [tx1_uuid]
