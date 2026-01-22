# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from typing import Any

import pytest
from graphql import build_schema
from graphql import introspection_from_schema
from mora.graphapi.schema import get_schema
from mora.graphapi.version import Version
from more_itertools import one


@pytest.mark.parametrize(
    "version,expected",
    (
        (Version.VERSION_26, "Registration"),
        (Version.VERSION_27, "ResponseRegistration"),
    ),
)
def test_schema(version: Version, expected: str) -> None:
    """Test that registrations on Response has the correct type."""
    schema_sdl = get_schema(version).as_str()
    schema = build_schema(schema_sdl)
    introspection = introspection_from_schema(schema)
    types = introspection["__schema"]["types"]

    def find_by_name(collection: list, name: str) -> Any:
        return one(element for element in collection if element["name"] == name)

    # Find the "Query" type in the GraphQL schema
    query = find_by_name(types, "Query")
    query_fields = query["fields"]
    # Find "facets" within its fields and assert its type
    facets = find_by_name(query_fields, "facets")
    facets_type = facets["type"]["ofType"]
    assert facets_type == {
        "kind": "OBJECT",
        "name": "FacetResponsePaged",
        "ofType": None,
    }

    # Find the "FacetResponsePaged" type in the GraphQL schema
    facets = find_by_name(types, "FacetResponsePaged")
    facets_fields = facets["fields"]
    # Find "objects" within its fields
    objects = find_by_name(facets_fields, "objects")
    objects_type = objects["type"]["ofType"]
    assert objects_type == {
        "kind": "LIST",
        "name": None,
        "ofType": {
            "kind": "NON_NULL",
            "name": None,
            "ofType": {"kind": "OBJECT", "name": "FacetResponse", "ofType": None},
        },
    }

    # Find the "FacetResponse" type in the GraphQL schema
    objects = find_by_name(types, "FacetResponse")
    objects_fields = objects["fields"]
    # Find "registrations" within its fields
    registrations = find_by_name(objects_fields, "registrations")
    registrations_type = registrations["type"]["ofType"]
    assert registrations_type == {
        "kind": "LIST",
        "name": None,
        "ofType": {
            "kind": "NON_NULL",
            "name": None,
            "ofType": {"kind": "OBJECT", "name": expected, "ofType": None},
        },
    }
