# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "resolver,expected_length",
    [
        ("classes", 39),
        ("facets", 18),
        ("itsystems", 3),
    ],
)
async def test_response_format(
    graphapi_post: GraphAPIPost,
    resolver: str,
    expected_length: int,
) -> None:
    """Test response format."""
    # Query under v6 schema
    query_v6 = f"""
        query FormatTestQueryV6 {{
          {resolver} {{
            objects {{
              uuid
              user_key
            }}
          }}
        }}
    """
    response_v6: GQLResponse = graphapi_post(query_v6, url="/graphql/v6")
    assert response_v6.errors is None
    objects_v6 = response_v6.data[resolver]["objects"]
    assert len(objects_v6) == expected_length

    # Query under v7 schema
    query_v7 = f"""
        query FormatTestQueryV7 {{
          {resolver} {{
            objects {{
              current {{
                uuid
                user_key
              }}
            }}
          }}
        }}
    """
    response_v7: GQLResponse = graphapi_post(query_v7, url="/graphql/v7")
    assert response_v7.errors is None
    objects_v7 = response_v7.data[resolver]["objects"]
    assert len(objects_v7) == expected_length

    # Assert data equivalence under unpacking
    assert objects_v6 == [x["current"] for x in objects_v7]

    # Running V6 query on V7 schema
    response = graphapi_post(query_v6, url="/graphql/v7")
    error = one(response.errors)
    assert "Cannot query field 'user_key' on type " in error["message"]

    # Running V7 query on V6 schema
    response = graphapi_post(query_v7, url="/graphql/v6")
    error = one(response.errors)
    assert "Cannot query field 'current' on type " in error["message"]
