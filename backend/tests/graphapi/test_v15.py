# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest
from more_itertools import first

from tests.conftest import GQLResponse


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_facet(graphapi_post: Callable) -> None:
    """Test create_facet v15 shim."""
    # create under v15 schema
    v15_input = {
        "input": {
            "user_key": "Test",
        }
    }
    create_v15 = """
        mutation TestFacetCreate($input: FacetCreateInput!) {
            facet_create(input: $input) {
                current {
                    user_key
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    # create under v16 schema
    v16_input = {
        "input": {
            "user_key": "Test",
            "validity": {
                "from": None,
                "to": None,
            },
        }
    }
    create_v16 = """
        mutation TestFacetCreate($input: FacetCreateInput!) {
            facet_create(input: $input) {
                current {
                    user_key
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    expected = v16_input["input"]

    # Test it
    response_v15: GQLResponse = graphapi_post(create_v15, v15_input, url="/graphql/v15")
    assert response_v15.errors is None
    assert response_v15.data["facet_create"]["current"] == expected

    response_v16: GQLResponse = graphapi_post(create_v16, v16_input, url="/graphql/v16")
    assert response_v16.errors is None
    assert response_v16.data["facet_create"]["current"] == expected

    # Running v15 create on v16 schema
    response: GQLResponse = graphapi_post(create_v15, v15_input, url="/graphql/v16")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )

    # Running v16 create on v15 schema
    response: GQLResponse = graphapi_post(create_v16, v16_input, url="/graphql/v15")
    error = first(response.errors)
    assert (
        "Field 'validity' is not defined by type 'FacetCreateInput'."
        in error["message"]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_update_facet(graphapi_post: Callable) -> None:
    """Test update_facet v15 shim."""
    # update under v15 schema
    v15_input = {
        "input": {
            "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
            "user_key": "Test",
        }
    }
    # Intentionally FacetCreateInput here
    update_v15 = """
        mutation TestFacetUpdate($input: FacetUpdateInput!) {
            facet_update(input: $input) {
                uuid
            }
        }
    """

    # update under v16 schema
    v16_input = {
        "input": {
            "uuid": "14466fb0-f9de-439c-a6c2-b3262c367da7",
            "user_key": "Test",
            "validity": {
                "from": None,
                "to": None,
            },
        }
    }
    update_v16 = """
        mutation TestFacetUpdate($input: FacetUpdateInput!) {
            facet_update(input: $input) {
                uuid
            }
        }
    """

    # Test it
    response_v15: GQLResponse = graphapi_post(update_v15, v15_input, url="/graphql/v15")
    assert response_v15.errors is None
    print(response_v15)
    assert response_v15.data["facet_update"]["uuid"] == v15_input["input"]["uuid"]

    response_v16: GQLResponse = graphapi_post(update_v16, v16_input, url="/graphql/v16")
    assert response_v16.errors is None
    assert response_v16.data["facet_update"]["uuid"] == v16_input["input"]["uuid"]

    # Running v15 update on v16 schema
    response: GQLResponse = graphapi_post(update_v15, v15_input, url="/graphql/v16")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )

    # Running v16 update on v15 schema
    response: GQLResponse = graphapi_post(update_v16, v16_input, url="/graphql/v15")
    error = first(response.errors)
    assert (
        "Field 'validity' is not defined by type 'FacetUpdateInput'."
        in error["message"]
    )
