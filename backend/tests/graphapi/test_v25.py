# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from graphql import build_schema
from graphql import introspection_from_schema
from mora.graphapi.schema import get_schema
from mora.graphapi.version import Version
from more_itertools import one

from ..conftest import GraphAPIPost

FRAGMENTLESS_QUERY = """
{
  registrations {
    objects {
      model
    }
  }
}
"""
FACET_FRAGMENT_QUERY = """
{
  registrations {
    objects {
      ... on FacetRegistration {
        model
      }
    }
  }
}
"""
CLASS_FRAGMENT_QUERY = """
{
  registrations {
    objects {
      ... on ClassRegistration {
        model
      }
    }
  }
}
"""
ERROR = "Fragment cannot be spread here as objects of type 'Registration' can never be of type 'FacetRegistration'."


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "query,url,expected",
    (
        # The fragmentless version of the query works on both versions
        (FRAGMENTLESS_QUERY, "/graphql/v25", {"model": "facet"}),
        (FRAGMENTLESS_QUERY, "/graphql/v26", {"model": "facet"}),
        # The facet fragment version of the query only works on v26
        (
            FACET_FRAGMENT_QUERY,
            "/graphql/v25",
            "Fragment cannot be spread here as objects of type 'Registration' can never be of type 'FacetRegistration'.",
        ),
        (FACET_FRAGMENT_QUERY, "/graphql/v26", {"model": "facet"}),
        # The class fragment version of the query only works on v26
        (
            CLASS_FRAGMENT_QUERY,
            "/graphql/v25",
            "Fragment cannot be spread here as objects of type 'Registration' can never be of type 'ClassRegistration'.",
        ),
        (CLASS_FRAGMENT_QUERY, "/graphql/v26", {}),
    ),
)
async def test_fragmental_queries(
    graphapi_post: GraphAPIPost,
    create_facet: Callable[[dict[str, Any]], UUID],
    query: str,
    url: str,
    expected: str | dict[str, Any],
) -> None:
    """Test fragmental queries on registrations."""
    create_facet(
        {
            "user_key": "facet_create",
            "validity": {"from": "1970-01-01"},
        }
    )

    response = graphapi_post(query, url=url)
    # If expected is a string, it is an error message
    if isinstance(expected, str):
        assert one(response.errors)["message"] == expected
        assert response.data is None
    else:  # Otherwise it is the expected data
        assert response.errors is None
        assert response.data is not None
        obj = one(response.data["registrations"]["objects"])
        assert obj == expected


@pytest.mark.parametrize(
    "version,expected",
    (
        (Version.VERSION_25, "RegistrationPaged"),
        (Version.VERSION_26, "IRegistrationPaged"),
    ),
)
def test_schema(version: Version, expected: str) -> None:
    """Test that registrations top-level has the correct type."""
    schema_sdl = get_schema(version).as_str()
    schema = build_schema(schema_sdl)
    introspection = introspection_from_schema(schema)
    types = introspection["__schema"]["types"]

    def find_by_name(collection: list, name: str) -> Any:
        return one(element for element in collection if element["name"] == name)

    # Find the "Query" type in the GraphQL schema
    query = find_by_name(types, "Query")
    # Find "registrations" within its fields
    query_fields = query["fields"]
    registrations = find_by_name(query_fields, "registrations")
    # Assert the return-type of "registrations" is the expected value
    registrations_type = registrations["type"]["ofType"]
    assert registrations_type == {"kind": "OBJECT", "name": expected, "ofType": None}
