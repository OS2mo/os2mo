# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Test the strip_args function."""

from inspect import signature
from typing import Any
from uuid import UUID

import pytest
from mora.graphapi.versions.latest.filters import BaseFilter
from mora.graphapi.versions.latest.resolvers import CursorType
from mora.graphapi.versions.latest.resolvers import LimitType
from mora.graphapi.versions.latest.seed_resolver import strip_args
from strawberry.types import Info


async def dummy_resolver(
    info: Info,
    filter: BaseFilter | None = BaseFilter(),
    limit: LimitType = 10,
    cursor: CursorType = None,
) -> Any:
    return {
        "info": info,
        "filter": filter,
        "limit": limit,
        "cursor": cursor,
    }


@pytest.mark.parametrize(
    "remove_parameters,expected_parameters",
    [
        # No remove, all arguments
        (None, {"info", "filter", "limit", "cursor"}),
        ({}, {"info", "filter", "limit", "cursor"}),
        # Remove single, keep the rest
        ({"filter"}, {"info", "limit", "cursor"}),
        ({"limit"}, {"info", "filter", "cursor"}),
        ({"cursor"}, {"info", "limit", "filter"}),
        # Remove two, keep the remaining
        ({"limit", "cursor"}, {"info", "filter"}),
        # Remove three, keep just one
        ({"filter", "limit", "cursor"}, {"info"}),
    ],
)
async def test_signature_changes(
    remove_parameters: set[str], expected_parameters: set[str]
) -> None:
    """Test that strip_args changes the call signature as expected.

    The signature is important as it used by strawberry to generate the GraphQL schema.

    Args:
        remove_parameters: The parameters to remove with strip_args.
        expected_parameters: The parameters to find after strip_args.
    """
    # Check the original signature
    original_resolver = dummy_resolver
    original_parameters = signature(original_resolver).parameters
    assert original_parameters.keys() == {"info", "filter", "limit", "cursor"}

    # Strip the arguments and check that we have the desired signature
    stripped_resolver = strip_args(original_resolver, remove_parameters)
    stripped_parameters = signature(stripped_resolver).parameters
    assert stripped_parameters.keys() == expected_parameters

    # Ensure we only replace the resolver when required to do so
    if original_parameters == stripped_parameters:
        assert original_resolver == stripped_resolver
    else:
        assert original_resolver != stripped_resolver


@pytest.mark.parametrize(
    "remove_parameters",
    [
        # Info and root are both reserved
        {"info"},
        {"root"},
        {"root", "info"},
        # Mixing in valid ones still fail
        {"info", "filter"},
        {"cursor", "limit", "root"},
    ],
)
async def test_protected_parameters(remove_parameters: set[str]) -> None:
    with pytest.raises(AssertionError) as exc_info:
        strip_args(dummy_resolver, remove_parameters)
    assert "Cannot remove parameter:" in str(exc_info.value)


@pytest.mark.parametrize(
    "remove_parameters",
    [
        # No remove, all arguments
        None,
        {},
        # Remove single, keep the rest
        {"filter"},
        {"limit"},
        {"cursor"},
        # Remove two, keep the remaining
        {"limit", "cursor"},
        # Remove three, keep just one
        {"filter", "limit", "cursor"},
    ],
)
async def test_call_values(remove_parameters: set[str]) -> None:
    """Test that calling a stripped function actually calls with default values.

    Args:
        remove_parameters: The parameters to remove with strip_args.
    """
    info = object()

    # Calling a stripped function sets the default values
    seeded = strip_args(dummy_resolver, remove_parameters)
    result = await seeded(info)
    assert result == {
        "info": info,
        "filter": BaseFilter(),
        "limit": 10,
        "cursor": None,
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": 2},
        {
            "cursor": "29fe33:eyJvZmZzZXQiOiAxLCAicmVnaXN0cmF0aW9uX3RpbWUiOiAiMjAyNS0xMC0zMFQxNjoxODoxOC4wMDg5ODkrMDE6MDAifQ=="
        },
        {"filter": BaseFilter(uuids=[UUID("9c407aa2-675a-4e0c-a761-7488f64a76b7")])},
        {"limit": 2, "filter": BaseFilter()},
    ],
)
async def test_call_with_removed_parameters(kwargs: Any) -> None:
    info = object()

    seeded = strip_args(dummy_resolver, {"filter", "limit", "cursor"})
    with pytest.raises(AssertionError) as exc_info:
        await seeded(info, **kwargs)
    assert "stripped_resolver called with removed key:" in str(exc_info.value)
