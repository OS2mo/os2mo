# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Test the seed_resolver function."""

import dataclasses
import typing
from collections.abc import Callable
from inspect import Parameter
from inspect import signature
from typing import Any

import pytest
from mora.graphapi.versions.latest.filters import BaseFilter
from mora.graphapi.versions.latest.resolvers import CursorType
from mora.graphapi.versions.latest.resolvers import LimitType
from mora.graphapi.versions.latest.seed_resolver import seed_resolver
from more_itertools import first
from strawberry.types import Info

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


async def dummy_resolver(
    info: Info,
    filter: BaseFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    return {
        "info": info,
        "filter": filter,
        "limit": limit,
        "cursor": cursor,
    }


@pytest.mark.parametrize(
    "seeds,expected_filter_fields",
    [
        ({}, {"uuids", "user_keys", "from_date", "to_date", "registration_time"}),
        (
            {"uuids": lambda _: 1},
            {"user_keys", "from_date", "to_date", "registration_time"},
        ),
        (
            {
                "user_keys": lambda _: ["test"],
                "from_date": lambda _: 1,
                "to_date": lambda _: 2,
                "registration_time": lambda _: 3,
            },
            {"uuids"},
        ),
    ],
)
async def test_signature_changes(
    seeds: dict[str, Any], expected_filter_fields: set[str]
) -> None:
    """Test that seed_resolver changes the call signature as expected.

    The signature is important as it used by strawberry to generate the GraphQL schema.

    Args:
        seeds: The seeds to set on seed_resolver.
    """
    # Check the original signature
    original_resolver = dummy_resolver
    original_parameters = signature(original_resolver).parameters
    assert original_parameters["filter"] == Parameter(
        "filter",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=BaseFilter | None,
        default=None,
    )

    # Seeding the resolver adds a root parameter and removes the seeded keys from the
    # filter.
    seeded_resolver = seed_resolver(original_resolver, seeds)
    seeded_paramters = signature(seeded_resolver).parameters
    assert seeded_paramters["root"] == Parameter(
        "root",
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Any,
    )
    seeded_filter_type = typing.get_args(seeded_paramters["filter"].annotation)
    seeded_filter_class = first(seeded_filter_type)  # strip `| None`
    seeded_filter_fields = {f.name for f in dataclasses.fields(seeded_filter_class)}
    assert seeded_filter_fields == expected_filter_fields


@pytest.mark.parametrize(
    "seeds,expected",
    [
        ({}, {}),
        ({"user_keys": lambda _: ["test"]}, {"user_keys": ["test"]}),
        (
            {"user_keys": lambda root: list(root.values())},
            {"user_keys": ["val1", "val2"]},
        ),
    ],
)
async def test_call_values(
    seeds: dict[str, Callable], expected: dict[str, Any]
) -> None:
    """Test that calling a seeded function actually calls with a seeded filter.

    Args:
        seeds: The seeds to set on seed_resolver.
        expected: The expected filter arguments when _resolve is called.
    """
    info = object()
    root = {
        "fake": "val1",
        "object": "val2",
    }

    # Calling a seeded function sets the value to the seed result
    seeded = seed_resolver(dummy_resolver, seeds=seeds)
    result = await seeded(info, root=root)
    assert result == {
        "info": info,
        "filter": BaseFilter(**expected),
        "limit": None,
        "cursor": None,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_nested_filters(graphapi_post: GraphAPIPost) -> None:
    """Test that seed_resolver doesn't break nested filters."""
    query = """
        query NestedRolesQuery {
          itusers(filter: {employee: {cpr_numbers: "0906340000"}, itsystem: {user_keys: "SAP"}}) {
            objects {
              current {
                person(filter: {from_date: "2001-02-03", to_date: null}) {
                  addresses(filter: {address_type: {user_keys: "BrugerEmail"}}) {
                    user_key
                  }
                }
              }
            }
          }
        }
    """
    result: GQLResponse = graphapi_post(query)
    assert result.errors is None
    assert result.data == {
        "itusers": {
            "objects": [
                {
                    "current": {
                        "person": [
                            {
                                "addresses": [{"user_key": "bruger@example.comw"}],
                            },
                        ]
                    }
                }
            ]
        }
    }
