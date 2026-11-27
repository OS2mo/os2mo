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
        # No filter: all current organisation units are returned.
        ({}, {"a1", "a2", "b1", "root_a", "root_b"}),
        # `not: null` does not filter anything.
        (
            {"from_date": None, "to_date": None, "not": None},
            {"a1", "a2", "b1", "past", "root_a", "root_b"},
        ),
        # An empty nested filter matches all current organisation units.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        (
            {"not": {"user_keys": ["nonexistent"]}},
            {"a1", "a2", "b1", "root_a", "root_b"},
        ),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1", "root_a", "root_b"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2", "root_a", "root_b"}),
        # Exclude by nested parent filter.
        ({"not": {"parent": {"user_keys": ["root_a"]}}}, {"b1", "root_a", "root_b"}),
        # The outer and the nested filter are combined.
        (
            {
                "parent": {"user_keys": ["root_a"]},
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"parent": {"user_keys": ["root_a"]}},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "parent": {"user_keys": ["root_a"]},
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current organisation units, so the past one is not excluded.
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
            {"a1", "a2", "b1", "root_a", "root_b"},
        ),
    ],
)
def test_org_unit_not_filter(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that organisation units can be excluded using a nested filter."""
    root_a = create_org_unit("root_a")
    root_b = create_org_unit("root_b")

    for user_key, parent, validity in [
        ("a1", root_a, {"from": "2020-01-01"}),
        ("a2", root_a, {"from": "2020-01-01"}),
        ("b1", root_b, {"from": "2020-01-01"}),
        ("past", root_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_org_unit(user_key, parent=parent, validity=validity)

    response = graphapi_post(
        """
        query ReadOrgUnits($filter: OrganisationUnitFilter) {
            org_units(filter: $filter) {
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
        for obj in response.data["org_units"]["objects"]
        for validity in obj["validities"]
    } == expected
