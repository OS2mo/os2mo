# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora.graphapi.shim import execute_graphql
from mora.service.util import handle_gql_error
from strawberry.exceptions import GraphQLError

from tests.conftest import GraphAPIPost

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
