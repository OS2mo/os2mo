# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import secrets

import pytest
from pytest import MonkeyPatch
from ramqp import AMQPSystem
from ramqp.mo import PayloadUUID
from starlette.testclient import TestClient

from mora.config import get_settings
from oio_rest.db import close_connection
from tests.conftest import GraphAPIPost


def create_employee(graphapi_post: GraphAPIPost, surname: str) -> str:
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
    return employee_uuid


def update_employee(graphapi_post: GraphAPIPost, uuid: str, surname: str) -> None:
    graphapi_post(
        """
        mutation Update($uuid: UUID!, $surname: String!) {
          employee_update(input: {uuid: $uuid, validity: {from: "2012-03-04"}, surname: $surname}) {
            uuid
          }
        }
        """,
        variables={
            "uuid": uuid,
            "surname": surname,
        },
    )


def read_employee_surname(graphapi_post: GraphAPIPost, uuid: str) -> str:
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
            "uuid": uuid,
        },
    )
    return employee.data["employees"]["objects"][0]["current"]["surname"]


@pytest.mark.integration_test
async def test_database_snapshot(
    monkeypatch: MonkeyPatch,
    raw_client: TestClient,
    graphapi_post: GraphAPIPost,
) -> None:
    # Clear singleton database connection, and ensure it is recreated as in a normally
    # running application, i.e. without the pytest TESTING environment variable.
    close_connection()
    monkeypatch.delenv("TESTING")

    # Create employee
    employee_uuid = create_employee(graphapi_post, surname="foo")
    assert read_employee_surname(graphapi_post, employee_uuid) == "foo"

    # Snapshot database
    assert raw_client.post("/testing/database/snapshot").is_success

    # Update surname
    update_employee(graphapi_post, uuid=employee_uuid, surname="bar")
    assert read_employee_surname(graphapi_post, employee_uuid) == "bar"

    # Restore to original surname
    assert raw_client.post("/testing/database/restore").is_success
    assert read_employee_surname(graphapi_post, employee_uuid) == "foo"

    # Close connection to ensure the next test will recreate it with settings expected
    # during testing.
    close_connection()


# NOTE: Read "backend/tests/graphapi/test_registration.py:11",
# for reasoning behind "@pytest.mark.xfail"


@pytest.mark.xfail
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_amqp_emit(
    raw_client: TestClient,
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

    is_called = asyncio.Event()
    callback_args = {}

    @amqp_system.router.register("person")
    async def callback(uuid: PayloadUUID) -> None:
        is_called.set()
        callback_args["uuid"] = uuid

    await amqp_system.start()

    # Create employee
    created_employee_uuid = create_employee(graphapi_post, surname="foo")

    # There should be no AMQP message
    await asyncio.sleep(1)
    assert not is_called.is_set()

    # Emit AMQP message
    assert raw_client.post("/testing/amqp/emit").is_success

    # We should be notified through AMQP
    await asyncio.wait_for(is_called.wait(), timeout=5)
    assert callback_args["uuid"] == created_employee_uuid
