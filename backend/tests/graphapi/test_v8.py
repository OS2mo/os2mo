# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import pytest

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "uuid",
    [
        "85715fc7-925d-401b-822d-467eb4b163b6",
        "b688513d-11f7-4efc-b679-ab082a2055d0",
        "fa2e23c9-860a-4c90-bcc6-2c0721869a25",
        "5942ce50-2be8-476f-914b-6769a888a7c8",
    ],
)
async def test_mutator_format(graphapi_post: GraphAPIPost, uuid: str) -> None:
    """Test terminate_org_unit v8 vs v9."""
    today = datetime.today().strftime("%Y-%m-%d")
    test_input = {"input": {"uuid": uuid, "to": today}}

    # Mutation under v8 schema
    mutation_v8 = """
        mutation TestTerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
            org_unit_terminate(unit: $input) {
                uuid
            }
        }
    """
    response_v8: GQLResponse = graphapi_post(mutation_v8, test_input, url="/graphql/v8")
    assert response_v8.errors is None
    assert response_v8.data["org_unit_terminate"] is not None

    # Mutation under v9 schema
    mutation_v9 = """
        mutation TestTerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
            org_unit_terminate(input: $input) {
                uuid
            }
        }
    """
    response_v9: GQLResponse = graphapi_post(mutation_v9, test_input, url="/graphql/v9")
    assert response_v9.errors is None
    assert response_v9.data["org_unit_terminate"] is not None

    # Running v8 mutation on v9 schema
    response = graphapi_post(mutation_v8, url="/graphql/v9")
    error = response.errors[0]
    assert (
        "Unknown argument 'unit' on field 'Mutation.org_unit_terminate'."
        in error["message"]
    )

    # Running v9 mutation on v8 schema
    response = graphapi_post(mutation_v9, url="/graphql/v8")
    error = response.errors[0]
    assert (
        "Unknown argument 'input' on field 'Mutation.org_unit_terminate'."
        in error["message"]
    )
