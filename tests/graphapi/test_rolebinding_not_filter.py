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
        # No filter: all current rolebindings are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current rolebindings.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2"}),
        # Exclude by nested role filter.
        ({"not": {"role": {"user_keys": ["role_a"]}}}, {"b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "role": {"user_keys": ["role_a"]},
                "not": {"user_keys": ["a1"]},
            },
            {"a2"},
        ),
        (
            {
                "user_keys": ["a1", "b1"],
                "not": {"role": {"user_keys": ["role_a"]}},
            },
            {"b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "role": {"user_keys": ["role_a"]},
                "not": {"user_keys": ["b1"]},
            },
            {"a1", "a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current rolebindings, so the past one is not excluded.
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
def test_rolebinding_not_filter(
    graphapi_post: GraphAPIPost,
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[..., UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that rolebindings can be excluded using a nested filter."""
    itsystem = create_itsystem(
        {"user_key": "itsystem", "name": "ITSystem", "validity": {"from": "2020-01-01"}}
    )
    role_a, role_b = (
        create_class(
            {
                "user_key": user_key,
                "name": user_key,
                "facet_uuid": str(role_facet),
                "it_system_uuid": str(itsystem),
                "validity": {"from": "2020-01-01"},
            }
        )
        for user_key in ("role_a", "role_b")
    )
    ituser = create_ituser(
        {
            "user_key": "ituser",
            "itsystem": str(itsystem),
            "person": str(create_person()),
            "validity": {"from": "2020-01-01"},
        }
    )

    for user_key, role, validity in [
        ("a1", role_a, {"from": "2020-01-01"}),
        ("a2", role_a, {"from": "2020-01-01"}),
        ("b1", role_b, {"from": "2020-01-01"}),
        ("past", role_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_rolebinding(
            {
                "user_key": user_key,
                "ituser": str(ituser),
                "role": str(role),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadRolebindings($filter: RoleBindingFilter) {
            rolebindings(filter: $filter) {
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
        for obj in response.data["rolebindings"]["objects"]
        for validity in obj["validities"]
    } == expected
