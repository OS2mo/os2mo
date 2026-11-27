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
        # No filter: all current IT systems are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current IT systems.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2"}),
        # Exclude a group of objects.
        ({"not": {"user_keys": ["a1", "a2"]}}, {"b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "user_keys": ["a1", "a2"],
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"user_keys": ["a1", "a2"]},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "user_keys": ["a1", "a2"],
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current IT systems, so the past one is not excluded.
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
def test_itsystem_not_filter(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that IT systems can be excluded using a nested filter."""
    for user_key, validity in [
        ("a1", {"from": "2020-01-01"}),
        ("a2", {"from": "2020-01-01"}),
        ("b1", {"from": "2020-01-01"}),
        ("past", {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_itsystem({"user_key": user_key, "name": user_key, "validity": validity})

    response = graphapi_post(
        """
        query ReadItsystems($filter: ITSystemFilter) {
            itsystems(filter: $filter) {
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
        for obj in response.data["itsystems"]["objects"]
        for validity in obj["validities"]
    } == expected
