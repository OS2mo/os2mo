# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "added_input, error_messages",
    [
        (
            {"given_name": None, "givenname": "John"},
            [
                "Field 'given_name' of required type 'String!' was not provided.",
                "Field 'givenname' is not defined by type 'EmployeeCreateInput'.",
            ],
        ),
        (
            {"given_name": None, "surname": None, "name": "John Deere"},
            [
                "Field 'given_name' of required type 'String!' was not provided.",
                "Field 'surname' of required type 'String!' was not provided.",
                "Field 'name' is not defined by type 'EmployeeCreateInput'.",
            ],
        ),
        (
            {"nickname": "Peter Smith"},
            ["Field 'nickname' is not defined by type 'EmployeeCreateInput'."],
        ),
        (
            {"cpr_no": "0101901111"},
            ["Field 'cpr_no' is not defined by type 'EmployeeCreateInput'."],
        ),
    ],
)
async def test_create_mutator_format(
    graphapi_post: GraphAPIPost, added_input: dict[str, Any], error_messages: list[str]
) -> None:
    """Test create_employee v12 vs v13."""
    test_input = {
        "input": {
            "given_name": "John",
            "surname": "Deere",
        }
    }
    test_input["input"].update(added_input)
    test_input["input"] = {k: v for k, v in test_input["input"].items() if v}

    mutation = """
        mutation TestCreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    response_v12: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v12")
    assert response_v12.errors is None
    assert response_v12.data["employee_create"] is not None

    response_v13: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v13")
    for error, expected in zip(response_v13.errors, error_messages):
        assert "Variable '$input' got invalid value" in error["message"]
        assert expected in error["message"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "added_input, error_messages",
    [
        (
            {"givenname": "John"},
            ["Field 'givenname' is not defined by type 'EmployeeUpdateInput'."],
        ),
        (
            {"name": "John Deere"},
            ["Field 'name' is not defined by type 'EmployeeUpdateInput'."],
        ),
        (
            {"nickname": "Peter Smith"},
            ["Field 'nickname' is not defined by type 'EmployeeUpdateInput'."],
        ),
        (
            {"cpr_no": "0101901111"},
            ["Field 'cpr_no' is not defined by type 'EmployeeUpdateInput'."],
        ),
        (
            {"validity": None, "from": "2020-01-01"},
            [
                "Field 'validity' of required type 'RAValidityInput!' was not provided.",
                "Field 'from' is not defined by type 'EmployeeUpdateInput'.",
            ],
        ),
        (
            {"validity": None, "from": "2020-01-01", "to": "2021-01-01"},
            [
                "Field 'validity' of required type 'RAValidityInput!' was not provided.",
                "Field 'from' is not defined by type 'EmployeeUpdateInput'.",
            ],
        ),
    ],
)
async def test_update_mutator_format(
    graphapi_post: GraphAPIPost, added_input: dict[str, Any], error_messages: list[str]
) -> None:
    """Test create_employee v12 vs v13."""
    test_input = {
        "input": {
            "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "validity": {"from": "2020-01-01"},
        }
    }
    test_input["input"].update(added_input)
    test_input["input"] = {k: v for k, v in test_input["input"].items() if v}

    mutation = """
        mutation TestUpdateEmployee($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
    """
    response_v12: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v12")
    assert response_v12.errors is None
    assert response_v12.data["employee_update"] is not None

    response_v13: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v13")
    for error, expected in zip(response_v13.errors, error_messages):
        assert "Variable '$input' got invalid value" in error["message"]
        assert expected in error["message"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "added_input, error_messages",
    [
        (
            {"name": "John Deere", "given_name": "John"},
            ["'name' is only allowed to be set, if 'given_name' & 'surname' are None."],
        ),
        (
            {"name": "John Deere", "givenname": "John"},
            ["'name' is only allowed to be set, if 'given_name' & 'surname' are None."],
        ),
        (
            {"name": "John Deere", "surname": "Deere"},
            ["'name' is only allowed to be set, if 'given_name' & 'surname' are None."],
        ),
        (
            {"given_name": "John", "givenname": "John"},
            ["'given_name' is only allowed to be set, if 'given_name' is None."],
        ),
        (
            {"cpr_no": "0101901111", "cpr_number": "0101901111"},
            ["'cpr_number' is only allowed to be set, if 'cpr_no' is None."],
        ),
        (
            {"nickname": "John Deere", "nickname_given_name": "John"},
            [
                "'nickname' is only allowed to be set, if 'nickname_given_name' & 'nickname_surname' are None."
            ],
        ),
        (
            {"nickname": "John Deere", "nickname_surname": "Deere"},
            [
                "'nickname' is only allowed to be set, if 'nickname_given_name' & 'nickname_surname' are None."
            ],
        ),
    ],
)
async def test_create_validators(
    graphapi_post: GraphAPIPost, added_input: dict[str, Any], error_messages: list[str]
) -> None:
    """Test create_employee v12 validators."""
    test_input = {"input": {"given_name": "John", "surname": "Deere"}}
    test_input["input"].update(added_input)

    mutation = """
        mutation TestCreateEmployee($input: EmployeeCreateInput!) {
            employee_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, test_input, url="/graphql/v12")
    assert response.data is None
    for error, expected in zip(response.errors, error_messages):
        assert expected in error["message"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "added_input, error_messages",
    [
        (
            {"name": "John Deere", "given_name": "John"},
            [
                'EmployeeUpdate.name is only allowed to be set, if "given_name" & "surname" are None.'
            ],
        ),
        (
            {"name": "John Deere", "givenname": "John"},
            [
                'EmployeeUpdate.name is only allowed to be set, if "given_name" & "surname" are None.'
            ],
        ),
        (
            {"name": "John Deere", "surname": "Deere"},
            [
                'EmployeeUpdate.name is only allowed to be set, if "given_name" & "surname" are None.'
            ],
        ),
        (
            {"given_name": "John", "givenname": "John"},
            ["'given_name' is only allowed to be set, if 'given_name' is None."],
        ),
        (
            {"cpr_no": "0101901111", "cpr_number": "0101901111"},
            ["'cpr_number' is only allowed to be set, if 'cpr_no' is None."],
        ),
        (
            {"nickname": "John Deere", "nickname_given_name": "John"},
            [
                "'nickname' is only allowed to be set, if 'nickname_given_name' & 'nickname_surname' are None."
            ],
        ),
        (
            {"nickname": "John Deere", "nickname_surname": "Deere"},
            [
                "'nickname' is only allowed to be set, if 'nickname_given_name' & 'nickname_surname' are None."
            ],
        ),
        (
            {"validity": {"from": "2020-01-01"}, "from": "2020-01-01"},
            ["Can only set one of 'validity' and 'from_date' / 'to_date'"],
        ),
        (
            {"validity": {"from": "2020-01-01"}, "to": "2020-01-01"},
            ["Can only set one of 'validity' and 'from_date' / 'to_date'"],
        ),
        (
            {"validity": None},
            ["Must set one of 'validity' and 'from_date' / 'to_date'"],
        ),
    ],
)
async def test_update_validators(
    graphapi_post: GraphAPIPost, added_input: dict[str, Any], error_messages: list[str]
) -> None:
    """Test update_employee v12 validators."""
    test_input = {
        "input": {
            "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "validity": {"from": "2020-01-01"},
        }
    }
    test_input["input"].update(added_input)

    mutation = """
        mutation TestUpdateEmployee($input: EmployeeUpdateInput!) {
            employee_update(input: $input) {
                uuid
            }
        }
    """

    response = graphapi_post(mutation, test_input, url="/graphql/v12")
    assert response.data is None
    for error, expected in zip(response.errors, error_messages):
        assert expected in error["message"]
