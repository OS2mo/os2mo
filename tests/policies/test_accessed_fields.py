# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the fields an operation is found to reach."""

import pytest
from graphql import parse

from mora.graphapi import schema
from mora.graphapi.policies import collect_accessed_fields
from mora.graphapi.schema import get_schema
from mora.graphapi.version import Version
from tests.conftest import GraphAPIPost


@pytest.fixture
def graphql_schema():
    return get_schema(max(Version))._schema


def test_collects_nested_fields_and_fragments(graphql_schema) -> None:
    """A field is collected wherever it is selected, fragments included."""
    document = parse("""
        query Employees($with_addresses: Boolean!) {
            employees {
                objects { ...validities }
            }
        }
        fragment validities on EmployeeResponse {
            validities {
                uuid
                addresses @include(if: $with_addresses) { value }
            }
        }
    """)

    accessed = collect_accessed_fields(graphql_schema, document)

    assert ("Query", "employees") in accessed
    assert ("EmployeeResponse", "validities") in accessed
    assert ("Employee", "uuid") in accessed
    # A field behind a directive is collected too: the operation may reach it
    assert ("Employee", "addresses") in accessed
    assert ("Address", "value") in accessed
    assert ("Employee", "cpr_number") not in accessed


def test_collects_the_implementations_of_an_interface(graphql_schema) -> None:
    """A resolver is handed the concrete type, so naming the interface is not enough."""
    document = parse("""
        query Addresses {
            addresses {
                objects { validities { resolve { __typename } } }
            }
        }
    """)

    accessed = collect_accessed_fields(graphql_schema, document)

    assert ("ResolvedAddress", "__typename") in accessed
    assert ("DefaultAddress", "__typename") in accessed
    assert ("DARAddress", "__typename") in accessed
    assert ("MultifieldAddress", "__typename") in accessed


def test_collects_mutation_fields(graphql_schema) -> None:
    """A mutator is gated like any other field."""
    document = parse("""
        mutation UpdateEmployee($input: EmployeeUpdateInput!) {
            employee_update(input: $input) { uuid }
        }
    """)

    accessed = collect_accessed_fields(graphql_schema, document)

    assert ("Mutation", "employee_update") in accessed
    # The mutator answers with a response type, whose own fields are gated too
    assert ("EmployeeResponse", "uuid") in accessed


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_a_field_the_walk_missed_is_an_error_not_a_denial(
    graphapi_post: GraphAPIPost, monkeypatch
) -> None:
    """A field missing from the plan is a bug in the walk, and says so."""
    monkeypatch.setattr(schema, "collect_accessed_fields", lambda *_: frozenset())

    response = graphapi_post("query { version { mo_version } }")

    assert response.errors is not None
    assert "No policy approved the access" not in str(response.errors)
