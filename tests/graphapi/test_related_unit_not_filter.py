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
        # No filter: all current related units are returned.
        ({}, {"ou_a <-> a1", "ou_a <-> a2", "ou_b <-> b1"}),
        # `not: null` does not filter anything.
        (
            {"from_date": None, "to_date": None, "not": None},
            {"ou_a <-> a1", "ou_a <-> a2", "ou_b <-> b1", "ou_b <-> past"},
        ),
        # An empty nested filter matches all current related units.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        (
            {"not": {"user_keys": ["nonexistent"]}},
            {"ou_a <-> a1", "ou_a <-> a2", "ou_b <-> b1"},
        ),
        # Exclude by user-key.
        ({"not": {"user_keys": ["ou_a <-> a1"]}}, {"ou_a <-> a2", "ou_b <-> b1"}),
        ({"not": {"user_keys": ["ou_a <-> a1", "ou_b <-> b1"]}}, {"ou_a <-> a2"}),
        # Exclude by nested org unit filter.
        ({"not": {"org_unit": {"user_keys": ["ou_a"]}}}, {"ou_b <-> b1"}),
        # The outer and the nested filter are combined.
        (
            {
                "org_unit": {"user_keys": ["ou_a"]},
                "not": {"user_keys": ["ou_a <-> a1"]},
            },
            {"ou_a <-> a2"},
        ),
        (
            {
                "user_keys": ["ou_a <-> a1", "ou_b <-> b1"],
                "not": {"org_unit": {"user_keys": ["ou_a"]}},
            },
            {"ou_b <-> b1"},
        ),
        # Excluding something outside the outer filter changes nothing.
        (
            {
                "org_unit": {"user_keys": ["ou_a"]},
                "not": {"user_keys": ["ou_b <-> b1"]},
            },
            {"ou_a <-> a1", "ou_a <-> a2"},
        ),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["ou_a <-> a1"]}}}, {"ou_a <-> a1"}),
        # The nested filter uses its own dates: by default it only matches
        # current related units, so the past one is not excluded.
        (
            {"from_date": None, "to_date": None, "not": {}},
            {"ou_b <-> past"},
        ),
        (
            {
                "from_date": None,
                "to_date": None,
                "not": {
                    "from_date": None,
                    "to_date": None,
                    "user_keys": ["ou_b <-> past"],
                },
            },
            {"ou_a <-> a1", "ou_a <-> a2", "ou_b <-> b1"},
        ),
    ],
)
def test_related_unit_not_filter(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that related units can be excluded using a nested filter."""
    ou_a = create_org_unit("ou_a")
    ou_b = create_org_unit("ou_b")
    a1 = create_org_unit("a1")
    a2 = create_org_unit("a2")
    b1 = create_org_unit("b1")
    past = create_org_unit("past")

    def relate(org_unit: UUID, related_org_unit: UUID, to_date: str | None) -> None:
        response = graphapi_post(
            """
            mutation CreateRelatedUnit($input: RelatedUnitCreateInput!) {
                related_unit_create(input: $input) {
                    uuid
                }
            }
            """,
            {
                "input": {
                    "org_unit": str(org_unit),
                    "related_org_unit": str(related_org_unit),
                    "validity": {"from": "2020-01-01", "to": to_date},
                }
            },
        )
        assert response.errors is None

    relate(ou_a, a1, None)
    relate(ou_a, a2, None)
    relate(ou_b, b1, None)
    relate(ou_b, past, "2020-12-31")

    response = graphapi_post(
        """
        query ReadRelatedUnits($filter: RelatedUnitFilter) {
            related_units(filter: $filter) {
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
        for obj in response.data["related_units"]["objects"]
        for validity in obj["validities"]
    } == expected
