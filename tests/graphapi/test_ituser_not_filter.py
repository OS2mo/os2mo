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
        # No filter: all current IT users are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current IT users.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2"}),
        # Exclude by nested IT system filter.
        ({"not": {"itsystem": {"user_keys": ["sys_a"]}}}, {"b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "itsystem": {"user_keys": ["sys_a"]},
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"itsystem": {"user_keys": ["sys_a"]}},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "itsystem": {"user_keys": ["sys_a"]},
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current IT users, so the past IT user is not excluded.
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
def test_ituser_not_filter(
    graphapi_post: GraphAPIPost,
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_person: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that IT users can be excluded using a nested filter."""
    sys_a = create_itsystem(
        {"user_key": "sys_a", "name": "A", "validity": {"from": "2020-01-01"}}
    )
    sys_b = create_itsystem(
        {"user_key": "sys_b", "name": "B", "validity": {"from": "2020-01-01"}}
    )
    person = create_person()

    for user_key, itsystem, validity in [
        ("a1", sys_a, {"from": "2020-01-01"}),
        ("a2", sys_a, {"from": "2020-01-01"}),
        ("b1", sys_b, {"from": "2020-01-01"}),
        ("past", sys_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_ituser(
            {
                "user_key": user_key,
                "itsystem": str(itsystem),
                "person": str(person),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadITUsers($filter: ITUserFilter) {
            itusers(filter: $filter) {
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
        for obj in response.data["itusers"]["objects"]
        for validity in obj["validities"]
    } == expected
