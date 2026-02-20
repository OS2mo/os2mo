# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from fastapi.encoders import jsonable_encoder
from mora import mapping
from mora.graphapi.versions.latest.models import EmployeeUpdate
from more_itertools import one

from ..conftest import GraphAPIPost

# Helpers

now_beginning = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
tz_cph = ZoneInfo("Europe/Copenhagen")
now_min_cph = datetime.combine(datetime.now().date(), datetime.min.time()).replace(
    tzinfo=tz_cph
)
invalid_uuids = [UUID("7626ad64-327d-481f-8b32-36c78eb12f8c")]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all our employees."""
    query = """
        query {
            employees {
                objects {
                    uuid
                    objects {
                        given_name
                        surname
                        nickname_given_name
                        nickname_surname
                        cpr_number
                        seniority
                        user_key
                        type
                        uuid
                        validity {from to}
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


@patch(
    "mora.service.employee.does_employee_with_cpr_already_exist", new_callable=AsyncMock
)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_employee_integration_test(
    does_employee_with_cpr_already_exist: AsyncMock,
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that employees can be created in LoRa via GraphQL."""

    does_employee_with_cpr_already_exist.return_value = False

    test_data = {
        "uuid": str(uuid4()),
        "given_name": "Integ",
        "surname": "Ration",
        "cpr_number": "0202020202",
        "user_key": "integ_user",
    }

    mutate_query = """
        mutation CreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})
    assert response.errors is None
    assert response.data is not None
    uuid = UUID(response.data["employee_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            employees(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        given_name
                        surname
                        cpr_number
                    }
                }
            }
        }
    """
    response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(one(response.data["employees"]["objects"])["objects"])
    assert obj["given_name"] == test_data["given_name"]
    assert obj["surname"] == test_data["surname"]
    assert obj["user_key"] == test_data["user_key"]
    assert obj["cpr_number"] == test_data["cpr_number"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_employee_with_nickname(graphapi_post) -> None:
    """Test that employees can be created with nicknames via GraphQL."""

    mutate_query = """
        mutation CreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
                current {
                    nickname_given_name
                    nickname_surname
                    given_name
                    surname
                }
            }
        }
    """
    input = {
        "given_name": "Garik",
        "surname": "Weinstein",
        "nickname_given_name": "Garry",
        "nickname_surname": "Kasparov",
    }
    response = graphapi_post(mutate_query, {"input": input})
    assert response.errors is None
    assert response.data is not None
    UUID(response.data["employee_create"]["uuid"])

    current = response.data["employee_create"]["current"]

    assert current["given_name"] == input["given_name"]
    assert current["surname"] == input["surname"]

    assert current["nickname_given_name"] == input["nickname_given_name"]
    assert current["nickname_surname"] == input["nickname_surname"]


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "given_mutator_args,given_error_msg_checks",
    [
        # CPR-No
        (
            {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", "cpr_number": ""},
            ["Expected type 'CPR'"],
        ),
        (
            {
                "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "cpr_number": "00112233445",
            },
            ["Expected type 'CPR'"],
        ),
        (
            {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", "cpr_number": "001122334"},
            ["Expected type 'CPR'"],
        ),
        (
            {"uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a", "cpr_number": "001"},
            ["Expected type 'CPR'"],
        ),
    ],
)
async def test_update_mutator_fails(
    given_mutator_args,
    given_error_msg_checks,
    graphapi_post: GraphAPIPost,
):
    """Test which verifies that certain mutator inputs, cause a validation error."""

    payload = {
        "uuid": given_mutator_args.get("uuid"),
        "validity": {"from": now_min_cph.isoformat()},
        "given_name": given_mutator_args.get("given_name"),
        "surname": given_mutator_args.get("surname"),
        "nickname_given_name": given_mutator_args.get("nickname_given_name"),
        "nickname_surname": given_mutator_args.get("nickname_surname"),
        "seniority": given_mutator_args.get("seniority"),
        "cpr_number": given_mutator_args.get("cpr_number"),
    }

    mutation_response = graphapi_post(
        """
        mutation($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
        """,
        {"input": payload},
    )

    assert mutation_response.errors is not None
    err_message = one(mutation_response.errors).get("message", "")

    for error_msg_check in given_error_msg_checks:
        assert re.search(error_msg_check, err_message)


@pytest.mark.parametrize(
    "given_data",
    [
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "user_key": "a-new-test-userkey",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "given_name": "Test Given Name",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "surname": "Duke",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "nickname_given_name": "Fancy Nickname Given Name",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "nickname_surname": "Lord Nick",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "seniority": now_min_cph.date().isoformat(),
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "cpr_number": "0101892147",
        },
        {
            "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            "given_name": "TestMan",
            "surname": "Duke",
            "nickname_given_name": "Test",
            "nickname_surname": "Lord",
            "seniority": now_min_cph.date().isoformat(),
            "cpr_number": "0101872144",
        },
    ],
)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_integration(given_data, graphapi_post: GraphAPIPost):
    # Create test data
    test_data = EmployeeUpdate(
        uuid=given_data.get("uuid"),
        user_key=given_data.get("user_key"),
        validity={"from": now_min_cph},
        given_name=given_data.get("given_name"),
        surname=given_data.get("surname"),
        nickname_given_name=given_data.get("nickname_given_name"),
        nickname_surname=given_data.get("nickname_surname"),
        seniority=given_data.get("seniority"),
        cpr_number=given_data.get("cpr_number"),
    )
    payload = jsonable_encoder(test_data)

    # Invoke mutation & and get updated employee UUID
    mutation_response = graphapi_post(
        """
        mutation($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
        """,
        {"input": payload},
    )
    assert mutation_response.errors is None
    test_data_uuid_updated = UUID(mutation_response.data["employee_update"]["uuid"])

    # Fetch employee and verify and updated version of the employee can be found
    verify_response = graphapi_post(
        _get_employee_verify_query(), {mapping.UUID: str(test_data_uuid_updated)}
    )
    assert verify_response.errors is None
    assert len(verify_response.data["employees"]["objects"]) > 0

    verify_data_employee = one(verify_response.data["employees"]["objects"])
    verify_data_employee_objs = verify_data_employee.get("objects", [])
    assert len(verify_data_employee_objs) > 1

    verify_data = None
    for e_obj in verify_data_employee_objs:
        if not e_obj.get("validity", {}).get("to"):
            verify_data = e_obj
            break
    assert verify_data is not None

    # Assert the employee have been updated with the specified test data
    if test_data.user_key:
        assert verify_data.get("user_key") == test_data.user_key

    if test_data.given_name:
        assert verify_data.get("given_name") == test_data.given_name

    if test_data.surname:
        assert verify_data.get("surname") == test_data.surname

    if test_data.seniority:
        assert verify_data.get("seniority") == test_data.seniority.isoformat()

    if test_data.cpr_number:
        assert verify_data.get("cpr_number") == test_data.cpr_number


def _get_employee_verify_query():
    return """
        query VerifyQuery($uuid: UUID!) {
          employees(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
            objects {
              uuid,
              objects {
                uuid
                user_key
                given_name
                surname
                nickname_given_name
                nickname_surname
                seniority
                cpr_number
                validity {
                  from
                  to
                }
              }
            }
          }
        }
    """
