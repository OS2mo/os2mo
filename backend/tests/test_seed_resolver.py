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
from more_itertools import first

from mora.graphapi.versions.latest.filters import BaseFilter
from mora.graphapi.versions.latest.resolvers import Resolver
from mora.graphapi.versions.latest.schema import seed_resolver
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


class DummyModel:
    """Dummy MOModel for testing."""


class DummyResolver(Resolver):
    """Dummy Resolver for testing."""

    def __init__(self):
        super().__init__(DummyModel)
        self.args = ()
        self.kwargs = {}

    async def _resolve(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return {}


@pytest.mark.parametrize(
    "seeds,expected_filter_fields",
    [
        ({}, {"uuids", "user_keys", "from_date", "to_date"}),
        ({"uuids": lambda _: 1}, {"user_keys", "from_date", "to_date"}),
        (
            {
                "user_keys": lambda _: ["test"],
                "from_date": lambda _: 1,
                "to_date": lambda _: 2,
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
    original_resolver = DummyResolver()
    original_parameters = signature(original_resolver.resolve).parameters
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
    resolver = DummyResolver()

    # Calling unseeded sets the expected kwargs
    assert resolver.args == ()
    assert resolver.kwargs == {}
    await resolver.resolve(info)
    assert resolver.args == ()
    assert resolver.kwargs == {
        "info": info,
        "filter": None,
        "limit": None,
        "cursor": None,
    }

    # Calling a seeded function sets the value to the seed result
    seeded = seed_resolver(resolver, seeds=seeds)
    await seeded(info, root=root)
    assert resolver.args == ()
    assert resolver.kwargs["filter"] == BaseFilter(**expected)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_nested_filters(graphapi_post: GraphAPIPost) -> None:
    """Test that seed_resolver doesn't break nested filters."""
    query = """
        query NestedRolesQuery {
          roles(filter: {employee: {cpr_numbers: "0906340000"}}) {
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
        "roles": {
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
