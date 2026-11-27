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
        # No filter: all current classes are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current classes.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2"}),
        # Exclude by nested facet filter.
        ({"not": {"facet": {"user_keys": ["facet_a"]}}}, {"b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "facet": {"user_keys": ["facet_a"]},
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"facet": {"user_keys": ["facet_a"]}},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "facet": {"user_keys": ["facet_a"]},
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current classes, so the past one is not excluded.
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
def test_class_not_filter(
    graphapi_post: GraphAPIPost,
    create_class: Callable[[dict[str, Any]], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that classes can be excluded using a nested filter."""
    facet_a = create_facet({"user_key": "facet_a", "validity": {"from": "2020-01-01"}})
    facet_b = create_facet({"user_key": "facet_b", "validity": {"from": "2020-01-01"}})

    for user_key, facet, validity in [
        ("a1", facet_a, {"from": "2020-01-01"}),
        ("a2", facet_a, {"from": "2020-01-01"}),
        ("b1", facet_b, {"from": "2020-01-01"}),
        ("past", facet_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_class(
            {
                "user_key": user_key,
                "name": user_key,
                "facet_uuid": str(facet),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadClasses($filter: ClassFilter) {
            classes(filter: $filter) {
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
        for obj in response.data["classes"]["objects"]
        for validity in obj["validities"]
    } == expected
