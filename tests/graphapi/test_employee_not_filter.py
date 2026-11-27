# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from ..conftest import GraphAPIPost

# Employees cannot end, so instead of a past employee, the "former" employee
# has a past engagement in ou_a.
IN_OU_A = {"engagement": {"org_unit": {"user_keys": ["ou_a"]}}}
EVER_IN_OU_A = {
    "from_date": None,
    "to_date": None,
    "engagement": {
        "from_date": None,
        "to_date": None,
        "org_unit": {"user_keys": ["ou_a"]},
    },
}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: all employees are returned.
        ({}, {"a1", "a2", "b1", "former"}),
        # `not: null` does not filter anything.
        ({"not": None}, {"a1", "a2", "b1", "former"}),
        # An empty nested filter matches all employees.
        ({"not": {}}, set()),
        # A nested filter matching nothing excludes nothing.
        ({"not": {"user_keys": ["nonexistent"]}}, {"a1", "a2", "b1", "former"}),
        # Exclude by user-key.
        ({"not": {"user_keys": ["a1"]}}, {"a2", "b1", "former"}),
        ({"not": {"user_keys": ["a1", "b1"]}}, {"a2", "former"}),
        # Exclude by nested engagement filter.
        ({"not": IN_OU_A}, {"b1", "former"}),
        ({"not": EVER_IN_OU_A}, {"b1"}),
        # The outer and the nested filter are combined.
        ({**IN_OU_A, "not": {"user_keys": ["a1"]}}, {"a2"}),
        ({"user_keys": ["a1", "b1"], "not": IN_OU_A}, {"b1"}),
        # Excluding something outside the outer filter changes nothing.
        ({**IN_OU_A, "not": {"user_keys": ["b1"]}}, {"a1", "a2"}),
        # The nested filter can itself be negated.
        ({"not": {"not": {"user_keys": ["a1"]}}}, {"a1"}),
        # The nested filter uses its own dates, independently of the outer
        # filter: by default it only matches current engagements.
        ({**EVER_IN_OU_A, "not": IN_OU_A}, {"former"}),
        ({**EVER_IN_OU_A, "not": EVER_IN_OU_A}, set()),
    ],
)
def test_employee_not_filter(
    graphapi_post: GraphAPIPost,
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that employees can be excluded using a nested filter."""
    ou_a = create_org_unit("ou_a")
    ou_b = create_org_unit("ou_b")

    for user_key, org_unit, validity in [
        ("a1", ou_a, {"from": "2020-01-01"}),
        ("a2", ou_a, {"from": "2020-01-01"}),
        ("b1", ou_b, {"from": "2020-01-01"}),
        ("former", ou_a, {"from": "2020-01-01", "to": "2020-12-31"}),
    ]:
        person = create_person(
            {"given_name": user_key, "surname": user_key, "user_key": user_key}
        )
        create_engagement(
            {
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "org_unit": str(org_unit),
                "person": str(person),
                "validity": validity,
            }
        )

    response = graphapi_post(
        """
        query ReadEmployees($filter: EmployeeFilter) {
            employees(filter: $filter) {
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
        for obj in response.data["employees"]["objects"]
        for validity in obj["validities"]
    } == expected
