# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: all current leaves are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current leaves.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2"}),
        # Exclude by nested employee filter.
        ({"not": {"employee": {"user_keys": ["person_a"]}}}, {"b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "employee": {"user_keys": ["person_a"]},
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"employee": {"user_keys": ["person_a"]}},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "employee": {"user_keys": ["person_a"]},
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current leaves, so the past one is not excluded.
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
def test_leave_not_filter(
    graphapi_post: GraphAPIPost,
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that leaves can be excluded using a nested filter."""
    org_unit = create_org_unit("ou")

    def create_person_with_engagement(user_key: str) -> tuple[UUID, UUID]:
        person = create_person(
            {"given_name": user_key, "surname": user_key, "user_key": user_key}
        )
        engagement = create_engagement(
            {
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "org_unit": str(org_unit),
                "person": str(person),
                "validity": {"from": "2020-01-01"},
            }
        )
        return person, engagement

    person_a = create_person_with_engagement("person_a")
    person_b = create_person_with_engagement("person_b")

    for user_key, (person, engagement), validity in [
        ("a1", person_a, {"from": "2020-01-01"}),
        ("a2", person_a, {"from": "2020-01-01"}),
        ("b1", person_b, {"from": "2020-01-01"}),
        ("past", person_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_leave(
            {
                "user_key": user_key,
                "leave_type": str(uuid4()),
                "person": str(person),
                "engagement": str(engagement),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadLeaves($filter: LeaveFilter) {
            leaves(filter: $filter) {
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
        for obj in response.data["leaves"]["objects"]
        for validity in obj["validities"]
    } == expected
