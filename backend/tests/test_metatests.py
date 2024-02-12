# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import pytest

from tests.conftest import GraphAPIPost

CPR_NUMBERS = [
    "0101501234",
    "0101501234",
]


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize("cpr", CPR_NUMBERS)
async def test_database_isolation(graphapi_post: GraphAPIPost, cpr: str) -> None:
    """Test that two different tests each access a clean database."""
    query = """
        query EmployeeQuery($cpr_numbers: [CPR!]) {
          employees(filter: {cpr_numbers: $cpr_numbers}) {
            objects {
              uuid
            }
          }
        }
    """
    # Ensure database is clean. This will fail if test aren't properly isolated.
    response = graphapi_post(query, {"cpr_numbers": CPR_NUMBERS})
    assert len(response.data["employees"]["objects"]) == 0

    # Create user
    mutation = """
        mutation EmployeeCreate($cpr_number: CPR!) {
          employee_create(
            input: {cpr_number: $cpr_number, given_name: "Foo", surname: "Bar"}
          ) {
            uuid
          }
        }
    """
    graphapi_post(mutation, {"cpr_number": cpr})

    # The database should now contain one employee
    response = graphapi_post(query, {"cpr_numbers": CPR_NUMBERS})
    assert len(response.data["employees"]["objects"]) == 1