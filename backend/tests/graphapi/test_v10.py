# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_mutator_format(graphapi_post: GraphAPIPost) -> None:
    """Test create_manager v10 vs v11."""
    test_input = {
        "input": {
            "type": "manager",
            "manager_level": "3c791935-2cfa-46b5-a12e-66f7f54e70fe",
            "manager_type": "0d72900a-22a4-4390-a01e-fd65d0e0999d",
            "responsibility": "93ea44f9-127c-4465-a34c-77d149e3e928",
            "org_unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "user_key": "Test",
            "validity": {"from": "2020-01-01"},
        },
    }

    mutation = """
        mutation TestCreateManager($input: ManagerCreateInput!) {
            manager_create(input: $input) {
                uuid
            }
        }
    """
    response_v10: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v10")
    assert response_v10.errors is None
    assert response_v10.data["manager_create"] is not None

    response_v11: GQLResponse = graphapi_post(mutation, test_input, url="/graphql/v11")
    error = response_v11.errors[0]
    assert "Variable '$input' got invalid value" in error["message"]
    assert (
        "Field 'type' is not defined by type 'ManagerCreateInput'." in error["message"]
    )
