# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import first

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_class(graphapi_post: GraphAPIPost) -> None:
    """Test create_class v16 shim."""

    # create under v16 schema
    v16_input = {
        "input": {
            "name": "Test",
            "user_key": "Test",
            "facet_uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
        }
    }
    create_v16 = """
        mutation TestClassCreate($input: ClassCreateInput!) {
            class_create(input: $input) {
                current {
                    name
                    user_key
                    facet_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    # create under v17 schema
    v17_input = {
        "input": {
            **v16_input["input"],
            "validity": {
                "from": None,
                "to": None,
            },
        }
    }
    create_v17 = """
        mutation TestClassCreate($input: ClassCreateInput!) {
            class_create(input: $input) {
                current {
                    name
                    user_key
                    facet_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    expected = v17_input["input"]

    # Test it
    response_v16: GQLResponse = graphapi_post(create_v16, v16_input, url="/graphql/v16")
    assert response_v16.errors is None
    assert response_v16.data["class_create"]["current"] == expected

    response_v17: GQLResponse = graphapi_post(create_v17, v17_input, url="/graphql/v17")
    assert response_v17.errors is None
    assert response_v17.data["class_create"]["current"] == expected

    # Running v16 create on v17 schema
    response = graphapi_post(create_v16, v16_input, url="/graphql/v17")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )

    # Running v17 create on v16 schema
    response = graphapi_post(create_v17, v17_input, url="/graphql/v16")
    error = first(response.errors)
    assert (
        "Field 'validity' is not defined by type 'ClassCreateInput'."
        in error["message"]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_class(graphapi_post: GraphAPIPost) -> None:
    """Test update_class v15 shim."""
    # update under v16 schema
    v16_input = {
        "input": {
            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
            "facet_uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
            "name": "Test",
            "user_key": "Test",
        }
    }
    # Intentionally ClassUpdateInput here
    update_v16 = """
        mutation TestClassUpdate($input: ClassUpdateInput!) {
            class_update(input: $input) {
                uuid
            }
        }
    """

    # update under v17 schema
    v17_input = {
        "input": {
            **v16_input["input"],
            "validity": {
                "from": None,
                "to": None,
            },
        }
    }
    update_v17 = """
        mutation TestClassUpdate($input: ClassUpdateInput!) {
            class_update(input: $input) {
                uuid
            }
        }
    """

    # Test it
    response_v16: GQLResponse = graphapi_post(update_v16, v16_input, url="/graphql/v16")
    assert response_v16.errors is None
    assert response_v16.data["class_update"]["uuid"] == v16_input["input"]["uuid"]

    response_v17: GQLResponse = graphapi_post(update_v17, v17_input, url="/graphql/v17")
    assert response_v17.errors is None
    assert response_v17.data["class_update"]["uuid"] == v17_input["input"]["uuid"]

    # Running v16 update on v17 schema
    response = graphapi_post(update_v16, v16_input, url="/graphql/v17")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'ValidityInput!' was not provided."
        in error["message"]
    )

    # Running v17 update on v16 schema
    response = graphapi_post(update_v17, v17_input, url="/graphql/v16")
    error = first(response.errors)
    assert (
        "Field 'validity' is not defined by type 'ClassUpdateInput'."
        in error["message"]
    )
