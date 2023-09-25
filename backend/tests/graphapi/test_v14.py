# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest
from more_itertools import first

from tests.conftest import GQLResponse


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_query_itsystems(graphapi_post: Callable) -> None:
    """Test update_employee v12 validators."""
    test_input = {"filter": {}}

    # query under v14 schema
    query_v14 = """
        query TestITSystemFtiler($filter: BaseFilter!) {
            itsystems(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """

    # query under v15 schema
    query_v15 = """
        query TestITSystemFtiler($filter: ITSystemFilter!) {
            itsystems(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """

    expected = [
        {"uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"},
        {"uuid": "14466fb0-f9de-439c-a6c2-b3262c367da7"},
        {"uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"},
    ]

    # Test it
    response_v14: GQLResponse = graphapi_post(query_v14, test_input, url="/graphql/v14")
    assert response_v14.errors is None
    assert response_v14.data["itsystems"]["objects"] == expected

    response_v15: GQLResponse = graphapi_post(query_v15, test_input, url="/graphql/v15")
    assert response_v15.errors is None
    assert response_v15.data["itsystems"]["objects"] == expected

    # Running v14 query on v15 schema
    response: GQLResponse = graphapi_post(query_v14, url="/graphql/v15")
    error = first(response.errors)
    assert (
        "Unknown type 'BaseFilter'. Did you mean 'ClassFilter', 'FacetFilter', "
        in error["message"]
    )

    # Running v15 query on v14 schema
    response: GQLResponse = graphapi_post(query_v15, url="/graphql/v14")
    error = first(response.errors)
    assert (
        "Variable '$filter' of type 'ITSystemFilter!' used in position expecting type 'BaseFilter'."
        in error["message"]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_itsystem(graphapi_post: Callable) -> None:
    """Test update_employee v12 validators."""
    # create under v14 schema
    v14_input = {
        "input": {
            "user_key": "Test",
            "name": "Test",
            "from": "1990-01-01T00:00:00+01:00",
            "to": None,
        }
    }
    create_v14 = """
        mutation TestITSystemCreate($input: ITSystemCreateInput!) {
            itsystem_create(input: $input) {
                current {
                    user_key
                    name
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    # create under v15 schema
    v15_input = {
        "input": {
            "user_key": "Test",
            "name": "Test",
            "validity": {
                "from": "1990-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    }
    create_v15 = """
        mutation TestITSystemCreate($input: ITSystemCreateInput!) {
            itsystem_create(input: $input) {
                current {
                    user_key
                    name
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    expected = v15_input["input"]

    # Test it
    response_v14: GQLResponse = graphapi_post(create_v14, v14_input, url="/graphql/v14")
    assert response_v14.errors is None
    assert response_v14.data["itsystem_create"]["current"] == expected

    response_v15: GQLResponse = graphapi_post(create_v15, v15_input, url="/graphql/v15")
    assert response_v15.errors is None
    assert response_v15.data["itsystem_create"]["current"] == expected

    # Running v14 create on v15 schema
    response: GQLResponse = graphapi_post(create_v14, v14_input, url="/graphql/v15")
    error = first(response.errors)
    assert (
        "Field 'validity' of required type 'RAOpenValidityInput!' was not provided."
        in error["message"]
    )

    # Running v15 create on v14 schema
    response: GQLResponse = graphapi_post(create_v15, v15_input, url="/graphql/v14")
    error = first(response.errors)
    assert (
        "Field 'validity' is not defined by type 'ITSystemCreateInput'."
        in error["message"]
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_update_itsystem(graphapi_post: Callable) -> None:
    """Test update_employee v12 validators."""
    # update under v14 schema
    v14_input = {
        "input": {
            "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
            "user_key": "Test",
            "name": "Test",
            "from": "1990-01-01T00:00:00+01:00",
            "to": None,
        }
    }
    # Intentionally ITSystemCreateInput here
    update_v14 = """
        mutation TestITSystemUpdate($input: ITSystemCreateInput!) {
            itsystem_update(input: $input) {
                current {
                    user_key
                    name
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    # update under v15 schema
    v15_input = {
        "input": {
            "uuid": "14466fb0-f9de-439c-a6c2-b3262c367da7",
            "user_key": "Test",
            "name": "Test",
            "validity": {
                "from": "1990-01-01T00:00:00+01:00",
                "to": None,
            },
        }
    }
    update_v15 = """
        mutation TestITSystemUpdate($input: ITSystemUpdateInput!) {
            itsystem_update(input: $input) {
                current {
                    user_key
                    name
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    expected = {**v15_input["input"]}
    del expected["uuid"]

    # Test it
    response_v14: GQLResponse = graphapi_post(update_v14, v14_input, url="/graphql/v14")
    assert response_v14.errors is None
    assert response_v14.data["itsystem_update"]["current"] == expected

    response_v15: GQLResponse = graphapi_post(update_v15, v15_input, url="/graphql/v15")
    assert response_v15.errors is None
    assert response_v15.data["itsystem_update"]["current"] == expected

    # Running v14 update on v15 schema
    response: GQLResponse = graphapi_post(update_v14, v14_input, url="/graphql/v15")
    error = first(response.errors)
    assert (
        "Variable '$input' of type 'ITSystemCreateInput!' used in position expecting type 'ITSystemUpdateInput!'."
        in error["message"]
    )

    # Running v15 update on v14 schema
    response: GQLResponse = graphapi_post(update_v15, v15_input, url="/graphql/v14")
    error = first(response.errors)
    assert (
        "Unknown type 'ITSystemUpdateInput'. Did you mean 'ITSystemCreateInput', 'ITUserUpdateInput', "
        in error["message"]
    )
