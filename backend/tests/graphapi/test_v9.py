# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "uuid",
    [
        "32547559-cfc1-4d97-94c6-70b192eff825",
        "bf65769c-5227-49b4-97c5-642cfbe41aa1",
    ],
)
async def test_mutator_format(graphapi_post: GraphAPIPost, uuid: str) -> None:
    """Test class_update v9 vs v10."""
    test_input = {
        "uuid": uuid,
        "input": {
            "uuid": uuid,
            "facet_uuid": "ef71fe9c-7901-48e2-86d8-84116e210202",
            "name": "Test",
            "user_key": "Test",
        },
    }

    # Mutation under v9 schema
    mutation_v9 = """
        mutation TestClassUpdate($input: ClassUpdateInput!, $uuid: UUID!) {
            class_update(input: $input, uuid: $uuid) {
                uuid
            }
        }
    """
    response_v9: GQLResponse = graphapi_post(mutation_v9, test_input, url="/graphql/v9")
    assert response_v9.errors is None
    assert response_v9.data["class_update"] is not None

    # Mutation under v10 schema
    mutation_v10 = """
        mutation TestClassUpdate($input: ClassUpdateInput!) {
            class_update(input: $input) {
                uuid
            }
        }
    """
    response_v10: GQLResponse = graphapi_post(
        mutation_v10, test_input, url="/graphql/v10"
    )
    assert response_v10.errors is None
    assert response_v10.data["class_update"] is not None

    # Running v9 mutation on v10 schema
    response = graphapi_post(mutation_v9, url="/graphql/v10")
    error = response.errors[0]
    assert (
        "Unknown argument 'uuid' on field 'Mutation.class_update'." in error["message"]
    )

    # Running v10 mutation on v9 schema
    response = graphapi_post(mutation_v10, url="/graphql/v9")
    error = response.errors[0]
    assert (
        "Field 'class_update' argument 'uuid' of type 'UUID!' is required, but it was not provided."
        in error["message"]
    )
