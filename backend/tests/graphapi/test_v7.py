# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "uuid",
    [
        "00e96933-91e4-42ac-9881-0fe1738b2e59",
        "414044e0-fe5f-4f82-be20-1e107ad50e80",
        "55848eca-4e9e-4f30-954b-78d55eec0441",
        "64ea02e2-8469-4c54-a523-3d46729e86a7",
        "a0fe7d43-1e0d-4232-a220-87098024b34d",
        "cd6008bc-1ad2-4272-bc1c-d349ef733f52",
        "e1a9cede-8c9b-4367-b628-113834361871",
        "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
    ],
)
async def test_mutator_format(graphapi_post: GraphAPIPost, uuid: str) -> None:
    """Get addresses."""
    today = datetime.today().strftime("%Y-%m-%d")
    test_input = {"input": {"uuid": uuid, "to": today}}

    # Mutation under v7 schema
    mutation_v7 = """
        mutation TestTerminateAddress($input: AddressTerminateInput!) {
            address_terminate(at: $input) {
                uuid
            }
        }
    """
    response_v7: GQLResponse = graphapi_post(mutation_v7, test_input, url="/graphql/v7")
    assert response_v7.errors is None
    assert response_v7.data["address_terminate"] is not None

    # Mutation under v8 schema
    mutation_v8 = """
        mutation TestTerminateAddress($input: AddressTerminateInput!) {
            address_terminate(input: $input) {
                uuid
            }
        }
    """
    response_v8: GQLResponse = graphapi_post(mutation_v8, test_input, url="/graphql/v8")
    assert response_v8.errors is None
    assert response_v8.data["address_terminate"] is not None

    # Running V7 mutation on V8 schema
    response = graphapi_post(mutation_v7, url="/graphql/v8")
    error = response.errors[0]
    assert (
        "Unknown argument 'at' on field 'Mutation.address_terminate'."
        in error["message"]
    )

    # Running V8 mutation on V7 schema
    response = graphapi_post(mutation_v8, url="/graphql/v7")
    error = response.errors[0]
    assert (
        "Unknown argument 'input' on field 'Mutation.address_terminate'."
        in error["message"]
    )
