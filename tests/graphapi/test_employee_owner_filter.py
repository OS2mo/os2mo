# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # The owner sub-filter is an `OwnerFilter`; filter by the owner person
        # through its own nested `owner` field.
        (
            {"owner": {"owner": {"user_keys": ["owner-1"]}}},
            {"owned-1", "owned-both"},
        ),
        (
            {"owner": {"owner": {"user_keys": ["owner-2"]}}},
            {"owned-2", "owned-both"},
        ),
        # The owner-person `user_keys` is OR'ed: owned by owner-1 OR owner-2.
        (
            {"owner": {"owner": {"user_keys": ["owner-1", "owner-2"]}}},
            {"owned-1", "owned-2", "owned-both"},
        ),
        # An owner that owns nobody.
        (
            {"owner": {"owner": {"user_keys": ["unowned"]}}},
            set(),
        ),
        # A non-existent owner.
        (
            {"owner": {"owner": {"user_keys": ["does-not-exist"]}}},
            set(),
        ),
        # An empty owner filter matches every employee that has any owner.
        (
            {"owner": {}},
            {"owned-1", "owned-2", "owned-both"},
        ),
        # The owner filter AND's with the rest of the employee filter: only
        # employees owned by owner-1 AND in the explicit user-key set.
        (
            {
                "owner": {"owner": {"user_keys": ["owner-1"]}},
                "user_keys": ["owned-both"],
            },
            {"owned-both"},
        ),
        (
            {"owner": {"owner": {"user_keys": ["owner-1"]}}, "user_keys": ["owned-2"]},
            set(),
        ),
    ],
)
def test_employee_owner_filter(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The employee `owner` filter returns the directly-owned employees.

    Ownership graph (owner person -> owned employees):
        owner-1 -> owned-1, owned-both
        owner-2 -> owned-2, owned-both
        unowned -> (owns nobody)
    """
    world = {
        user_key: create_person(
            {"user_key": user_key, "given_name": given_name, "surname": surname}
        )
        for user_key, given_name, surname in [
            ("owner-1", "Olivia", "Owner"),
            ("owner-2", "Oscar", "Owner"),
            ("owned-1", "Edith", "Employee"),
            ("owned-2", "Egon", "Employee"),
            ("owned-both", "Elin", "Employee"),
            ("unowned", "Ulla", "Unowned"),
        ]
    }

    def own(owned: str, owner: str) -> None:
        create_owner(
            {
                "person": str(world[owned]),
                "owner": str(world[owner]),
                "validity": {"from": "2020-01-01T00:00:00+01:00"},
            }
        )

    own("owned-1", "owner-1")
    own("owned-2", "owner-2")
    own("owned-both", "owner-1")
    own("owned-both", "owner-2")

    actual = read_employee_uuids(filter)
    assert actual == {world[user_key] for user_key in expected}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_owner_filter_is_directional(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
) -> None:
    """`owner` matches the owned side, never the owner side."""
    owner = create_person({"given_name": "Olivia", "surname": "Owner"})
    employee = create_person({"given_name": "Edith", "surname": "Employee"})
    create_owner(
        {
            "person": str(employee),
            "owner": str(owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )

    # `owner` is an employee too, but filtering by it returns the owned side.
    actual = read_employee_uuids({"owner": {"owner": {"uuids": [str(owner)]}}})
    assert owner not in actual
    assert actual == {employee}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_owner_filter_by_owner_function(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
) -> None:
    """The owner sub-filter is an `OwnerFilter`, so the owned employee can be
    selected by the owner org-function's own uuid.
    """
    owner = create_person({"given_name": "Owns", "surname": "Person"})
    employee = create_person({"given_name": "Owned", "surname": "Person"})
    owner_function = create_owner(
        {
            "person": str(employee),
            "owner": str(owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )

    actual = read_employee_uuids({"owner": {"uuids": [str(owner_function)]}})
    assert actual == {employee}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "employee_from,owner_from,matches",
    [
        # By default both gates are evaluated as of now, where they have expired.
        (None, None, False),
        # Both set within the validity period: the employee is matched.
        ("2020-06-01T00:00:00+01:00", "2020-06-01T00:00:00+01:00", True),
        # Only the ownership link is dated back; the owner org-function is still
        # evaluated as of now (expired) -> no match.
        ("2020-06-01T00:00:00+01:00", None, False),
        # Only the owner org-function is dated back; the ownership link is still
        # evaluated as of now (expired) -> no match.
        (None, "2020-06-01T00:00:00+01:00", False),
        # Both outside the validity period.
        ("2023-06-01T00:00:00+01:00", "2023-06-01T00:00:00+01:00", False),
    ],
)
def test_employee_owner_filter_respects_validity(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    employee_from: str | None,
    owner_from: str | None,
    matches: bool,
) -> None:
    """The owner relation is only matched within its validity period.

    The owner sub-filter carries its own validity, so a historical ownership
    query must set `from_date` on both the employee filter (which gates the
    ownership link) and the nested owner filter (which gates the owner
    org-function itself).
    """
    owner = create_person({"given_name": "Temp", "surname": "Owner"})
    employee = create_person({"given_name": "Temp", "surname": "Owned"})
    create_owner(
        {
            "person": str(employee),
            "owner": str(owner),
            "validity": {
                "from": "2020-01-01T00:00:00+01:00",
                "to": "2020-12-31T00:00:00+01:00",
            },
        }
    )

    # The ownership link (outer employee filter) and the owner org-function
    # itself (the `OwnerFilter`) are gated by separate `from_date`s; both must
    # fall within the validity period for a match.
    employee_filter: dict[str, Any] = {"owner": {"owner": {"uuids": [str(owner)]}}}
    if employee_from is not None:
        employee_filter["from_date"] = employee_from
    if owner_from is not None:
        employee_filter["owner"]["from_date"] = owner_from

    actual = read_employee_uuids(employee_filter)
    assert actual == ({employee} if matches else set())


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_employee_owner_filter_nested(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
) -> None:
    """The owner sub-filter recurses: an employee's owner can itself be filtered
    by who owns them.
    """
    grand_owner = create_person({"given_name": "Grand", "surname": "Owner"})
    owner = create_person({"given_name": "Mid", "surname": "Owner"})
    employee = create_person({"given_name": "Leaf", "surname": "Employee"})

    # grand_owner owns owner; owner owns employee.
    create_owner(
        {
            "person": str(owner),
            "owner": str(grand_owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )
    create_owner(
        {
            "person": str(employee),
            "owner": str(owner),
            "validity": {"from": "2020-01-01T00:00:00+01:00"},
        }
    )

    # Employees whose owner is in turn owned by grand_owner -> {employee}.
    actual = read_employee_uuids(
        {"owner": {"owner": {"owner": {"owner": {"uuids": [str(grand_owner)]}}}}}
    )
    assert actual == {employee}
