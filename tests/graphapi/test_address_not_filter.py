# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: all current addresses are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current addresses.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2"}),
        # Exclude by nested org unit filter.
        ({"not": {"org_unit": {"user_keys": ["ou_a"]}}}, {"b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "org_unit": {"user_keys": ["ou_a"]},
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"org_unit": {"user_keys": ["ou_a"]}},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "org_unit": {"user_keys": ["ou_a"]},
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current addresses, so the past one is not excluded.
        (
            {"from_date": None, "to_date": None, "not": {}},
            {"past"},
        ),
        (
            {
                "from_date": None,
                "to_date": None,
                "not": {"from_date": None, "to_date": None, "user_keys": ["past"]},
            },
            {"a1", "a2", "b1"},
        ),
    ],
)
def test_address_not_filter(
    graphapi_post: GraphAPIPost,
    create_address: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that addresses can be excluded using a nested filter."""
    # address_create reads the address_type class's `scope`, so we need
    # a real one.
    facet = create_facet(
        {"user_key": "org_unit_address_type", "validity": {"from": "2020-01-01"}}
    )
    address_type = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "email",
            "name": "Email",
            "scope": "EMAIL",
            "validity": {"from": "2020-01-01"},
        }
    )
    ou_a = create_org_unit("ou_a")
    ou_b = create_org_unit("ou_b")

    for user_key, org_unit, validity in [
        ("a1", ou_a, {"from": "2020-01-01"}),
        ("a2", ou_a, {"from": "2020-01-01"}),
        ("b1", ou_b, {"from": "2020-01-01"}),
        ("past", ou_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_address(
            {
                "user_key": user_key,
                "address_type": str(address_type),
                "value": f"{user_key}@example.org",
                "org_unit": str(org_unit),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadAddresses($filter: AddressFilter) {
            addresses(filter: $filter) {
                objects {
                    validities(start: null, end: null) {
                        user_key
                    }
                }
            }
        }
        """,
        {"filter": filter},
    )
    assert response.errors is None
    assert response.data
    assert {
        validity["user_key"]
        for obj in response.data["addresses"]["objects"]
        for validity in obj["validities"]
    } == expected
