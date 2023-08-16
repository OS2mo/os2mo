# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest
from pytest import MonkeyPatch
from starlette.testclient import TestClient

from oio_rest.db import close_connection
from tests.conftest import GQLResponse


def create_employee(graphapi_post: Callable[..., GQLResponse], surname: str) -> str:
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


def update_employee(
    graphapi_post: Callable[..., GQLResponse], uuid: str, surname: str
) -> None:
    graphapi_post(
        """
        mutation Update($uuid: UUID!, $surname: String!) {
          employee_update(input: {uuid: $uuid, from: "2012-03-04", surname: $surname}) {
            uuid
          }
        }
        """,
        variables={
            "uuid": uuid,
            "surname": surname,
        },
    )


def read_employee_surname(graphapi_post: Callable[..., GQLResponse], uuid: str) -> str:
    employee = graphapi_post(
        """
        query Read($uuid: UUID!) {
          employees(uuids: [$uuid]) {
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
async def test_rollback(
    monkeypatch: MonkeyPatch,
    raw_client: TestClient,
    graphapi_post: Callable[..., GQLResponse],
) -> None:
    # Clear singleton database connection, and ensure it is recreated as in a normally
    # running application, i.e. without the pytest TESTING environment variable.
    close_connection()
    monkeypatch.delenv("TESTING")

    # Disable autocommit
    raw_client.post("/testing/autocommit", params={"enable": False})

    # Create and commit employee
    employee_uuid = create_employee(graphapi_post, surname="foo")
    raw_client.post("/testing/commit")
    assert read_employee_surname(graphapi_post, employee_uuid) == "foo"

    # Update surname without committing
    update_employee(graphapi_post, uuid=employee_uuid, surname="bar")
    assert read_employee_surname(graphapi_post, employee_uuid) == "bar"

    # Rollback to committed value
    raw_client.post("/testing/rollback")
    assert read_employee_surname(graphapi_post, employee_uuid) == "foo"

    # Close connection to ensure the next test will recreate it with settings expected
    # during testing.
    close_connection()
