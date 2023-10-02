# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_mutator_format(graphapi_post: GraphAPIPost) -> None:
    """Test create_ituser v11 vs v12."""
    test_input = {
        "input": {
            "type": "it",
            "itsystem": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "user_key": "Test",
            "validity": {"from": "2020-01-01"},
        },
    }

    mutation = """
        mutation TestCreateituser($input: ITUserCreateInput!) {
            ituser_create(input: $input) {
                uuid
            }
        }
    """
    response_v11: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v11")
    assert response_v11.errors is None
    assert response_v11.data["ituser_create"] is not None

    response_v12: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v12")
    error = response_v12.errors[0]
    assert "Variable '$input' got invalid value" in error["message"]
    assert (
        "Field 'type' is not defined by type 'ITUserCreateInput'." in error["message"]
    )
