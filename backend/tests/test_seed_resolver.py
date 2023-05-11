# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Test the seed_resolver function."""
from collections.abc import Callable
from functools import partial
from inspect import Parameter
from inspect import signature
from typing import Any
from uuid import UUID

import pytest
from pydantic import PositiveInt
from strawberry.types.info import Info

from mora.graphapi.versions.latest.resolvers import StaticResolver
from mora.graphapi.versions.latest.schema import seed_resolver
from mora.graphapi.versions.latest.types import Cursor


class DummyModel:
    """Dummy MOModel for testing."""


class DummyResolver(StaticResolver):
    """Dummy StaticResolver for testing."""

    def __init__(self):
        super().__init__(DummyModel)
        self.args = ()
        self.kwargs = {}

    async def _resolve(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return []


def dict_remove_keys(
    dictionary: dict[str, Any], remove_keys: list[str]
) -> dict[str, Any]:
    """Returns a dictionary with the provided keys removed.

    Note:
        The returned dictionary is a shallow-copy of the original dictionary.

    Args:
        dictionary: The dictionary to remove keys from.
        remove_keys: The list of keys to remove.

    Return:
        New dictionary with keys removed.
    """
    return {key: value for key, value in dictionary.items() if key not in remove_keys}


@pytest.mark.parametrize(
    "seeds",
    [
        {},
        {"limit": lambda _: 1},
        {"cursor": lambda _: 2},
        {
            "user_keys": lambda _: ["test"],
            "limit": lambda _: 1,
            "cursor": lambda _: 2,
        },
    ],
)
async def test_signature_changes(seeds: dict[str, Any]) -> None:
    """Test that seed_resolver changes the call signature as expected.

    The signature is important as it used by strawberry to generate the GraphQL schema.

    Args:
        seeds: The seeds to set on seed_resolver.
    """
    pos_parameter = partial(Parameter, kind=Parameter.POSITIONAL_OR_KEYWORD)
    resolver_params = {
        "info": pos_parameter("info", annotation=Info),
        "uuids": pos_parameter("uuids", annotation=list[UUID] | None, default=None),
        "user_keys": pos_parameter(
            "user_keys", annotation=list[str] | None, default=None
        ),
        "limit": pos_parameter("limit", annotation=PositiveInt | None, default=None),
        "cursor": pos_parameter("cursor", annotation=Cursor | None, default=None),
    }

    # Check the signature
    resolver = DummyResolver()
    resolve = signature(resolver.resolve)
    assert list(resolve.parameters.values()) == list(resolver_params.values())

    # Seeding the resolver, adds a root parameter and removes the seeded keys
    resolver_params = {
        "root": pos_parameter("root", annotation=Any),
        **dict_remove_keys(resolver_params, list(seeds.keys())),
    }
    seeded = signature(seed_resolver(resolver, seeds))
    assert list(seeded.parameters.values()) == list(resolver_params.values())


@pytest.mark.parametrize(
    "seeds,expected",
    [
        ({"__non_existing_key": lambda _: ["failure"]}, "'__non_existing_key'"),
        (
            {
                "__non_existing_key1": lambda _: ["failure"],
                "__non_existing_key2": lambda _: ["failure"],
            },
            "'__non_existing_key1'",
        ),
        (
            {"limit": lambda _: 1, "__non_existing_key2": lambda _: ["failure"]},
            "'__non_existing_key2'",
        ),
    ],
)
async def test_signature_invalid_key(seeds: dict[str, Callable], expected: str) -> None:
    """Test that seeding a function with illegal seeds throw an exception.

    Args:
        seeds: The seeds to set on seed_resolver.
        expected: The expected error message.
    """
    resolver = DummyResolver()

    with pytest.raises(KeyError) as exc_info:
        seed_resolver(resolver, seeds)
    assert expected in str(exc_info.value)


@pytest.mark.parametrize(
    "seeds,expected",
    [
        ({}, {}),
        ({"limit": lambda _: 1}, {"limit": 1}),
        ({"cursor": lambda _: 2}, {"cursor": 2}),
        ({"user_keys": lambda _: ["test"]}, {"user_keys": ["test"]}),
        (
            {"user_keys": lambda root: list(root.values())},
            {"user_keys": ["val1", "val2"]},
        ),
        (
            {
                "user_keys": lambda _: ["test"],
                "limit": lambda _: 1,
                "cursor": lambda _: 2,
            },
            {
                "limit": 1,
                "cursor": 2,
                "user_keys": ["test"],
            },
        ),
    ],
)
async def test_call_values(
    seeds: dict[str, Callable], expected: dict[str, Any]
) -> None:
    """Test that calling a seeded function actually calls with seeded values.

    Args:
        seeds: The seeds to set on seed_resolver.
        expected: The expected kwargs overrides when _resolve is called.
    """
    info = object()
    root = {
        "fake": "val1",
        "object": "val2",
    }
    resolver = DummyResolver()

    # Calling resolve calls _resolve with expected parameters
    _resolver_kwargs = {
        "info": info,
        "uuids": None,
        "user_keys": None,
        "limit": None,
        "cursor": None,
        "from_date": None,
        "to_date": None,
    }

    assert resolver.args == ()
    assert resolver.kwargs == {}

    # Calling unseeded sets the expected kwargs
    await resolver.resolve(info)
    assert resolver.args == ()
    assert resolver.kwargs == _resolver_kwargs

    # Calling a seeded function sets the value to the seed result
    seeded = seed_resolver(resolver, seeds=seeds)
    await seeded(info, root=root)
    assert resolver.args == ()
    assert resolver.kwargs == {**_resolver_kwargs, **expected}
