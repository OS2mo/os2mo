# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import first

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_terminate_facet(graphapi_post: GraphAPIPost) -> None:
    """Test terminate_facet v18 shim."""
    mutation = """
        mutation TestFacetTerminate($input: FacetTerminateInput!) {
            facet_terminate(input: $input) {
                current {
                    uuid
                }
            }
        }
    """

    # terminate under v18 schema
    v18_entity_uuid = "ef71fe9c-7901-48e2-86d8-84116e210202"
    v18_input = {"input": {"uuid": v18_entity_uuid, "validity": {"to": "2023-01-01"}}}

    # terminate under v19 schema
    v19_entity_uuid = "baddc4eb-406e-4c6b-8229-17e4a21d3550"
    v19_input = {
        "input": {
            "uuid": v19_entity_uuid,
            "to": "2023-01-01",
        }
    }

    # Test it
    response_v18: GQLResponse = graphapi_post(mutation, v18_input, url="/graphql/v18")
    assert response_v18.errors is None
    assert response_v18.data["facet_terminate"]["current"] is None

    response_v19: GQLResponse = graphapi_post(mutation, v19_input, url="/graphql/v19")
    assert response_v19.errors is None
    assert response_v19.data["facet_terminate"]["current"] is None

    # Running v18 terminate on v19 schema
    response = graphapi_post(mutation, v18_input, url="/graphql/v19")
    error = first(response.errors)
    assert (
        "Field 'to' of required type 'DateTime!' was not provided." in error["message"]
    )

    # Running v19 terminate on v18 schema
    response = graphapi_post(mutation, v19_input, url="/graphql/v18")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_terminate_class(graphapi_post: GraphAPIPost) -> None:
    """Test terminate_class v18 shim."""
    mutation = """
        mutation TestClassTerminate($input: ClassTerminateInput!) {
            class_terminate(input: $input) {
                current {
                    uuid
                }
            }
        }
    """

    # terminate under v18 schema
    v18_entity_uuid = "32547559-cfc1-4d97-94c6-70b192eff825"
    v18_input = {"input": {"uuid": v18_entity_uuid, "validity": {"to": "2023-01-01"}}}

    # terminate under v19 schema
    v19_entity_uuid = "bf65769c-5227-49b4-97c5-642cfbe41aa1"
    v19_input = {
        "input": {
            "uuid": v19_entity_uuid,
            "to": "2023-01-01",
        }
    }

    # Test it
    response_v18: GQLResponse = graphapi_post(mutation, v18_input, url="/graphql/v18")
    assert response_v18.errors is None
    assert response_v18.data["class_terminate"]["current"] is None

    response_v19: GQLResponse = graphapi_post(mutation, v19_input, url="/graphql/v19")
    assert response_v19.errors is None
    assert response_v19.data["class_terminate"]["current"] is None

    # Running v18 terminate on v19 schema
    response = graphapi_post(mutation, v18_input, url="/graphql/v19")
    error = first(response.errors)
    assert (
        "Field 'to' of required type 'DateTime!' was not provided." in error["message"]
    )

    # Running v19 terminate on v18 schema
    response = graphapi_post(mutation, v19_input, url="/graphql/v18")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_terminate_itsystem(graphapi_post: GraphAPIPost) -> None:
    """Test terminate_itsystem v18 shim."""
    mutation = """
        mutation TestITSystemTerminate($input: ITSystemTerminateInput!) {
            itsystem_terminate(input: $input) {
                current {
                    uuid
                }
            }
        }
    """

    # terminate under v18 schema
    v18_entity_uuid = "59c135c9-2b15-41cc-97c8-b5dff7180beb"
    v18_input = {"input": {"uuid": v18_entity_uuid, "validity": {"to": "2023-01-01"}}}

    # terminate under v19 schema
    v19_entity_uuid = "0872fb72-926d-4c5c-a063-ff800b8ee697"
    v19_input = {
        "input": {
            "uuid": v19_entity_uuid,
            "to": "2023-01-01",
        }
    }

    # Test it
    response_v18: GQLResponse = graphapi_post(mutation, v18_input, url="/graphql/v18")
    assert response_v18.errors is None
    assert response_v18.data["itsystem_terminate"]["current"] is None

    response_v19: GQLResponse = graphapi_post(mutation, v19_input, url="/graphql/v19")
    assert response_v19.errors is None
    assert response_v19.data["itsystem_terminate"]["current"] is None

    # Running v18 terminate on v19 schema
    response = graphapi_post(mutation, v18_input, url="/graphql/v19")
    error = first(response.errors)
    assert (
        "Field 'to' of required type 'DateTime!' was not provided." in error["message"]
    )

    # Running v19 terminate on v18 schema
    response = graphapi_post(mutation, v19_input, url="/graphql/v18")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )
