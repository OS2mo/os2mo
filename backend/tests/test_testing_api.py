# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import secrets
from uuid import UUID

import pytest
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.mo import PayloadUUID
from mora.config import get_settings
from starlette.testclient import TestClient

from tests.conftest import GraphAPIPost


def create_employee(graphapi_post: GraphAPIPost, surname: str) -> UUID:
    employee = graphapi_post(
        """
        mutation Create($surname: String!) {
          employee_create(input: {given_name: "Foo", surname: $surname}) {
            uuid
          }
        }
        """,
        variables={
            "surname": surname,
        },
    )
    employee_uuid = employee.data["employee_create"]["uuid"]
    return UUID(employee_uuid)


def update_employee(graphapi_post: GraphAPIPost, uuid: UUID, surname: str) -> None:
    graphapi_post(
        """
        mutation Update($uuid: UUID!, $surname: String!) {
          employee_update(input: {uuid: $uuid, validity: {from: "2012-03-04"}, surname: $surname}) {
            uuid
          }
        }
        """,
        variables={
            "uuid": str(uuid),
            "surname": surname,
        },
    )


def read_employee_surname(graphapi_post: GraphAPIPost, uuid: UUID) -> str:
    employee = graphapi_post(
        """
        query Read($uuid: UUID!) {
          employees(filter: {uuids: [$uuid]}) {
            objects {
              current {
                surname
              }
            }
          }
        }
        """,
        variables={
            "uuid": str(uuid),
        },
    )
    return employee.data["employees"]["objects"][0]["current"]["surname"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_database_snapshot(
    admin_client: TestClient, graphapi_post: GraphAPIPost
) -> None:
    # Create employee
    employee_uuid = create_employee(graphapi_post, surname="foo")
    assert read_employee_surname(graphapi_post, employee_uuid) == "foo"

    # Snapshot database
    assert admin_client.post("/testing/database/snapshot").is_success

    # Update surname
    update_employee(graphapi_post, uuid=employee_uuid, surname="bar")
    assert read_employee_surname(graphapi_post, employee_uuid) == "bar"

    # Restore to original surname
    assert admin_client.post("/testing/database/restore").is_success
    assert read_employee_surname(graphapi_post, employee_uuid) == "foo"


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_amqp_emit(
    admin_client: TestClient,
    graphapi_post: GraphAPIPost,
) -> None:
    # Set up AMQP callback
    settings = get_settings()
    amqp_settings = settings.amqp.copy(
        update=dict(
            # A queue prefix is required when registering callbacks
            queue_prefix=secrets.token_hex(),
        ),
    )
    amqp_system = AMQPSystem(amqp_settings)

    uuids = set()

    @amqp_system.router.register("person")
    async def callback(uuid: PayloadUUID) -> None:
        uuids.add(uuid)

    await amqp_system.start()

    # Emit and clear AMQP messages for the fixture data employees
    assert admin_client.post("/testing/amqp/emit").is_success
    await asyncio.sleep(1)
    uuids.clear()

    # Create employee
    created_employee_uuid = create_employee(graphapi_post, surname="foo")

    # We should not be notified yet
    await asyncio.sleep(1)
    assert not uuids

    # Emit AMQP message
    assert admin_client.post("/testing/amqp/emit").is_success

    # We should be notified through AMQP
    await asyncio.sleep(1)
    assert created_employee_uuid in uuids
