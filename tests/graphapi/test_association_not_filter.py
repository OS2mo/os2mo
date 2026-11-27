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
        # No filter: all current associations are returned.
        ({}, {"a1", "a2", "b1"}),
        # `not: null` does not filter anything.
        ({"from_date": None, "to_date": None, "not": None}, {"a1", "a2", "b1", "past"}),
        # An empty nested filter matches all current associations.
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
        # current associations, so the past one is not excluded.
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
def test_association_not_filter(
    graphapi_post: GraphAPIPost,
    create_association: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that associations can be excluded using a nested filter."""
    ou_a = create_org_unit("ou_a")
    ou_b = create_org_unit("ou_b")
    person = create_person()

    for user_key, org_unit, validity in [
        ("a1", ou_a, {"from": "2020-01-01"}),
        ("a2", ou_a, {"from": "2020-01-01"}),
        ("b1", ou_b, {"from": "2020-01-01"}),
        ("past", ou_b, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        create_association(
            {
                "user_key": user_key,
                "association_type": str(uuid4()),
                "org_unit": str(org_unit),
                "employee": str(person),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadAssociations($filter: AssociationFilter) {
            associations(filter: $filter) {
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
        for obj in response.data["associations"]["objects"]
        for validity in obj["validities"]
    } == expected
