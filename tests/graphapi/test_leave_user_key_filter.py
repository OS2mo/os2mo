# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.fixture
def read_leave_user_keys(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[str]]:
    def inner(filter: dict[str, Any]) -> set[str]:
        response = graphapi_post(
            """
                query ReadLeaves($filter: LeaveFilter) {
                    leaves(filter: $filter) {
                        objects {
                            current {
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
        return {
            obj["current"]["user_key"]
            for obj in response.data["leaves"]["objects"]
        }

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # Filter shape edge cases
        ({}, {"leave_a", "leave_b", "leave_in_two", "leave_orphan"}),
        ({"user_keys": None}, {"leave_a", "leave_b", "leave_in_two", "leave_orphan"}),
        ({"user_keys": []}, set()),
        ({"user_keys": ["nonexistent"]}, set()),
        # Single user_key → its leave
        ({"user_keys": ["alpha"]}, {"leave_a"}),
        ({"user_keys": ["beta"]}, {"leave_b"}),
        ({"user_keys": ["gamma"]}, {"leave_in_two"}),
        # OR semantics
        ({"user_keys": ["alpha", "gamma"]}, {"leave_a", "leave_in_two"}),
        # Nested filters
        (
            {"employee": {"user_keys": ["employee1"]}},
            {"leave_a", "leave_b"},
        ),
        (
            {"org_unit": {"user_keys": ["ou1"]}},
            {"leave_a", "leave_orphan"},
        ),
        # AND-combine with sibling filters
        (
            {
                "user_keys": ["alpha", "gamma"],
                "employee": {"user_keys": ["employee1"]},
            },
            {"leave_a"},
        ),
        (
            {
                "user_keys": ["alpha"],
                "org_unit": {"user_keys": ["ou2"]},
            },
            set(),
        ),
    ],
)
def test_leave_user_key_filter(
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    read_leave_user_keys: Callable[[dict[str, Any]], set[str]],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Filter leaves by user_key."""
    ou1 = create_org_unit("ou1")
    ou2 = create_org_unit("ou2")
    employee1 = create_person()
    employee2 = create_person()

    engagement_a = create_engagement(
        {
            "user_key": "eng_a",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou1),
            "person": str(employee1),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )
    engagement_b = create_engagement(
        {
            "user_key": "eng_b",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou1),
            "person": str(employee1),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )
    engagement_in_two = create_engagement(
        {
            "user_key": "eng_in_two",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou2),
            "person": str(employee2),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )
    engagement_orphan = create_engagement(
        {
            "user_key": "eng_orphan",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou1),
            "person": str(employee2),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    leave_type = str(uuid4())

    leaves: dict[str, UUID] = {}
    for user_key, engagement, employee in [
        ("leave_a", engagement_a, employee1),
        ("leave_b", engagement_b, employee1),
        ("leave_in_two", engagement_in_two, employee2),
        ("leave_orphan", engagement_orphan, employee2),
    ]:
        leave_input: dict[str, Any] = {
            "user_key": user_key,
            "leave_type": leave_type,
            "engagement": str(engagement),
            "person": str(employee),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
        leaves[user_key] = create_leave(leave_input)

    assert read_leave_user_keys(filter) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_leave_filter_by_user_key_uuid(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
) -> None:
    """Filtering by leave UUID returns the correct leave.

    Verifies the round-trip: filtering by UUID returns the expected leave
    with matching user_key.
    """
    ou = create_org_unit("ou")
    person = create_person()

    engagement = create_engagement(
        {
            "user_key": "eng",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou),
            "person": str(person),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    leave_type = str(uuid4())
    leave = create_leave(
        {
            "user_key": "test_leave",
            "leave_type": leave_type,
            "engagement": str(engagement),
            "person": str(person),
            "validity": {"from": "1970-01-01"},
        }
    )

    response = graphapi_post(
        """
            query ReadLeave($uuid: UUID!) {
                leaves(filter: {uuids: [$uuid]}) {
                    objects {
                        current {
                            user_key
                        }
                    }
                }
            }
        """,
        variables={"uuid": str(leave)},
    )
    assert response.errors is None
    assert response.data
    obj = one(response.data["leaves"]["objects"])
    assert obj["current"]["user_key"] == "test_leave"

    response = graphapi_post(
        """
            query ReadLeaves($filter: LeaveFilter) {
                leaves(filter: $filter) {
                    objects {
                        uuid
                    }
                }
            }
        """,
        variables={"filter": {"uuids": [str(leave)]}},
    )
    assert response.errors is None
    assert response.data
    assert {UUID(o["uuid"]) for o in response.data["leaves"]["objects"]} == {leave}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_leave_user_key_filter_no_leak_across_registrations(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    read_leave_user_keys: Callable[[dict[str, Any]], set[str]],
) -> None:
    """An old leave registration must not leak user_key matches.

    Scenario:
      - Leave X initially has user_key "old_key".
      - Leave X later updated to user_key "new_key".
      - Filtering leaves by user_key "new_key" must yield only {X}, never {old_key, new_key}.
    """
    ou = create_org_unit("ou")
    person = create_person()

    engagement = create_engagement(
        {
            "user_key": "eng",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou),
            "person": str(person),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    leave_type = str(uuid4())
    leave = create_leave(
        {
            "user_key": "old_key",
            "leave_type": leave_type,
            "engagement": str(engagement),
            "person": str(person),
            "validity": {"from": "1970-01-01"},
        }
    )

    assert read_leave_user_keys({"user_keys": ["old_key"]}) == {"old_key"}
    assert read_leave_user_keys({"user_keys": ["new_key"]}) == set()

    response = graphapi_post(
        """
            mutation UpdateLeave($input: LeaveUpdateInput!) {
                leave_update(input: $input) {
                    uuid
                }
            }
        """,
        {
            "input": {
                "uuid": str(leave),
                "user_key": "new_key",
                "validity": {"from": "2000-01-01"},
            }
        },
    )
    assert response.errors is None

    assert read_leave_user_keys({"user_keys": ["old_key"]}) == set()
    assert read_leave_user_keys({"user_keys": ["new_key"]}) == {"new_key"}
