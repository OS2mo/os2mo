# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GQLResponse


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_mutator_extended_exception(graphapi_post) -> None:
    """Test that ServiceAPI exception context is exposed in GraphQL."""

    mutate_query = """
        mutation UpdateAddress($input: AddressUpdateInput!) {
            address_update(input: $input) {
                uuid
            }
        }
    """
    input = {
        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
        "validity": {"from": "2000-01-01", "to": None},
        "value": "12345678",
    }
    response: GQLResponse = graphapi_post(mutate_query, {"input": input})

    assert response.data is None
    assert response.errors == [
        {
            "extensions": {
                "error_context": {
                    "description": "Missing address_type",
                    "error": True,
                    "error_key": "V_MISSING_REQUIRED_VALUE",
                    "key": "address_type",
                    "obj": input,
                    "status": 400,
                }
            },
            "locations": [{"column": 13, "line": 3}],
            "message": "ErrorCodes.V_MISSING_REQUIRED_VALUE",
            "path": ["address_update"],
        }
    ]
