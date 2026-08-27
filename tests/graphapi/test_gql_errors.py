# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from starlette_context import context
from starlette_context import request_cycle_context
from strawberry.exceptions import GraphQLError

from mora.graphapi.shim import execute_graphql
from mora.service.util import handle_gql_error
from tests.conftest import GraphAPIPost
from tests.conftest import admin_token_getter

query = """
    query TestMultipleErrors {
      itsystems {
        objects {
          current {
            _non_existent_field_1
            _non_existent_field_2
          }
        }
      }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_multiple_errors(graphapi_post: GraphAPIPost) -> None:
    """Test how multiple errors are handled."""

    response = graphapi_post(query)
    assert response.errors == [
        {
            "locations": [{"column": 13, "line": 6}],
            "message": "Cannot query field '_non_existent_field_1' on type 'ITSystem'.",
        },
        {
            "locations": [{"column": 13, "line": 7}],
            "message": "Cannot query field '_non_existent_field_2' on type 'ITSystem'.",
        },
    ]
    assert response.data is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_handle_gql_errors() -> None:
    """Test how handle_gql_errors handles multiple exceptions."""

    # Nobody is calling us, so run as admin
    with request_cycle_context({**context, "get_token": admin_token_getter()}):
        response = await execute_graphql(query)
    with pytest.raises(ExceptionGroup) as exc_info:  # noqa: F821
        handle_gql_error(response)

    assert exc_info.value.message == "GraphQL Errors"

    exceptions = exc_info.value.exceptions
    assert len(exceptions) == 2

    assert isinstance(exceptions[0], GraphQLError)
    assert (
        exceptions[0].message
        == "Cannot query field '_non_existent_field_1' on type 'ITSystem'."
    )

    assert isinstance(exceptions[1], GraphQLError)
    assert (
        exceptions[1].message
        == "Cannot query field '_non_existent_field_2' on type 'ITSystem'."
    )


single_error_query = """
    query TestSingleError {
      itsystems {
        objects {
          current {
            _non_existent_field
          }
        }
      }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_handle_gql_error_single() -> None:
    """A single GraphQL error is raised as-is rather than grouped."""

    # Nobody is calling us, so run as admin
    with request_cycle_context({**context, "get_token": admin_token_getter()}):
        response = await execute_graphql(single_error_query)
    with pytest.raises(GraphQLError) as exc_info:
        handle_gql_error(response)

    assert (
        exc_info.value.message
        == "Cannot query field '_non_existent_field' on type 'ITSystem'."
    )


resolver_error_query = """
    mutation TriggerResolverError($input: RelatedUnitsUpdateInput!) {
      related_units_update(input: $input) { uuid }
    }
"""

resolver_error_variables = {
    "input": {
        "origin": "2874e1dc-85e6-4269-823a-e1125484dfd3",
        "destination": ["00000000-0000-0000-0000-000000000000"],
        "validity": {"from": "2017-01-01T00:00:00+01:00"},
    }
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_handle_gql_error_with_original_error() -> None:
    """Errors raised by resolvers carry an original_error which is unwrapped."""

    # Nobody is calling us, so run as admin
    with request_cycle_context({**context, "get_token": admin_token_getter()}):
        response = await execute_graphql(
            resolver_error_query, variable_values=resolver_error_variables
        )
    assert response.errors is not None
    with pytest.raises(Exception) as exc_info:
        handle_gql_error(response)
    # The unwrapped original error is raised (not the GraphQL wrapper)
    assert not isinstance(exc_info.value, GraphQLError)
