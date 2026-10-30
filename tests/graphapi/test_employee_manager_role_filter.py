# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # Every employee with a managerial role in the given org-unit
        (
            {"manager_role": {"org_unit": {"user_keys": ["A"]}}},
            {"anna", "carl"},
        ),
        # Every employee with a managerial role of the given type
        (
            {"manager_role": {"manager_type": {"user_keys": ["director"]}}},
            {"anna", "carl"},
        ),
        # Every employee with a managerial role with the given responsibility
        (
            {"manager_role": {"responsibility": {"user_keys": ["hr"]}}},
            {"anna"},
        ),
        # The manager role filter must be matched by a single role: carl heads A and
        # directs B, but is not the director of A
        (
            {
                "manager_role": {
                    "org_unit": {"user_keys": ["A"]},
                    "manager_type": {"user_keys": ["director"]},
                }
            },
            {"anna"},
        ),
        # A managerial role can also be selected by its own user-key
        (
            {"manager_role": {"user_keys": ["carl-head-A"]}},
            {"carl"},
        ),
        # Non-existent org-unit
        (
            {"manager_role": {"org_unit": {"user_keys": ["does-not-exist"]}}},
            set(),
        ),
        # An empty manager role filter matches every employee that has any
        # managerial role, so `dora`, who has none, is never returned
        (
            {"manager_role": {}},
            {"anna", "bob", "carl"},
        ),
        # `null` is the inverse of `{}`: only employees without any managerial
        # role
        (
            {"manager_role": None},
            {"dora"},
        ),
        # `null` AND's with the rest of the employee filter like any other
        # clause, so an employee that has a managerial role is still excluded
        (
            {"manager_role": None, "user_keys": ["anna"]},
            set(),
        ),
        (
            {"manager_role": None, "user_keys": ["dora"]},
            {"dora"},
        ),
        # The manager role filter AND's with the rest of the employee filter
        (
            {
                "manager_role": {"org_unit": {"user_keys": ["A"]}},
                "user_keys": ["carl"],
            },
            {"carl"},
        ),
        (
            {
                "manager_role": {"org_unit": {"user_keys": ["A"]}},
                "user_keys": ["bob"],
            },
            set(),
        ),
    ],
)
def test_employee_manager_role_filter(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_manager_raw: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The employee `manager_role` filter returns the employees holding the roles.

    Managerial roles (employee -> manager type, org-unit, responsibilities):
        anna -> director, A, hr
        bob  -> head, B, it
        carl -> head, A
        carl -> director, B
        dora -> (has no managerial role)
    """
    org_units = {user_key: create_org_unit(user_key) for user_key in ["A", "B"]}

    facets = {
        "manager_type": create_facet(
            {"user_key": "manager_type", "validity": {"from": "1970-01-01"}}
        ),
        "responsibility": create_facet(
            {"user_key": "responsibility", "validity": {"from": "1970-01-01"}}
        ),
    }
    classes = {
        user_key: create_class(
            {
                "user_key": user_key,
                "name": user_key,
                "facet_uuid": str(facets[facet]),
                "validity": {"from": "1970-01-01"},
            }
        )
        for facet, user_key in [
            ("manager_type", "director"),
            ("manager_type", "head"),
            ("responsibility", "hr"),
            ("responsibility", "it"),
        ]
    }

    world = {
        user_key: create_person(
            {"user_key": user_key, "given_name": given_name, "surname": surname}
        )
        for user_key, given_name, surname in [
            ("anna", "Anna", "Andersen"),
            ("bob", "Bob", "Bertelsen"),
            ("carl", "Carl", "Carlsen"),
            ("dora", "Dora", "Davidsen"),
        ]
    }

    for person, manager_type, org_unit, responsibilities in [
        ("anna", "director", "A", ["hr"]),
        ("bob", "head", "B", ["it"]),
        ("carl", "head", "A", []),
        ("carl", "director", "B", []),
    ]:
        create_manager_raw(
            {
                "user_key": f"{person}-{manager_type}-{org_unit}",
                "manager_level": str(uuid4()),
                "manager_type": str(classes[manager_type]),
                "responsibility": [str(classes[r]) for r in responsibilities],
                "org_unit": str(org_units[org_unit]),
                "person": str(world[person]),
                "validity": {"from": "2020-01-01T00:00:00+01:00"},
            }
        )

    expected = {world[user_key] for user_key in expected}
    actual = read_employee_uuids(filter)
    assert actual == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # Vacant roles make nobody a manager
        (
            {"manager_role": {}},
            {"holder"},
        ),
        # Nor do they exclude anybody from `null`, although the vacated role
        # stores its person as `NULL`
        (
            {"manager_role": None},
            {"former"},
        ),
        # `employee: null` selects the vacant roles, which nobody holds
        (
            {"manager_role": {"employee": None}},
            set(),
        ),
    ],
)
def test_employee_manager_role_filter_vacant_roles(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    update_manager: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Vacant managerial roles are held by nobody.

    A role created vacant has no person relation at all, while vacating a held
    role stores its person as `NULL` from then on.

    Managerial roles (employee -> role):
        holder -> held
        former -> vacated, held until 1980
        (none) -> created vacant
    """
    org_unit = create_org_unit("root")

    world = {
        "holder": create_person({"given_name": "Holder", "surname": "Manager"}),
        "former": create_person({"given_name": "Former", "surname": "Manager"}),
    }

    create_manager(org_unit, world["holder"])
    update_manager(create_manager(org_unit, world["former"]))
    create_manager(org_unit)

    expected = {world[user_key] for user_key in expected}
    actual = read_employee_uuids(filter)
    assert actual == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # By default the filter is evaluated as of now, where both have expired
        (
            {"manager_role": {"user_keys": ["manager-temp"]}},
            set(),
        ),
        # Both the relation and the manager org-function are dated back
        (
            {
                "manager_role": {
                    "user_keys": ["manager-temp"],
                    "from_date": "2020-06-01T00:00:00+01:00",
                },
                "from_date": "2020-06-01T00:00:00+01:00",
            },
            {"temp"},
        ),
        # Only the relation is dated back; the manager org-function is not
        (
            {
                "manager_role": {"user_keys": ["manager-temp"]},
                "from_date": "2020-06-01T00:00:00+01:00",
            },
            set(),
        ),
        # Only the manager org-function is dated back; the relation is not
        (
            {
                "manager_role": {
                    "user_keys": ["manager-temp"],
                    "from_date": "2020-06-01T00:00:00+01:00",
                }
            },
            set(),
        ),
        # Both outside the validity period
        (
            {
                "manager_role": {
                    "user_keys": ["manager-temp"],
                    "from_date": "2023-06-01T00:00:00+01:00",
                },
                "from_date": "2023-06-01T00:00:00+01:00",
            },
            set(),
        ),
    ],
)
def test_employee_manager_role_filter_respects_validity(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_manager_raw: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The manager role relation is only matched within its validity period.

    Managerial roles (employee -> user-key, validity):
        temp  -> manager-temp,  2020-01-01 to 2020-12-31
        other -> manager-other, 2020-01-01 to 2021-12-31

    `other` is unrelated to every filter and must never show up in the result.
    """
    org_unit = create_org_unit("root")

    world = {
        "temp": create_person({"given_name": "Temp", "surname": "Employee"}),
        "other": create_person({"given_name": "Other", "surname": "Employee"}),
    }

    for person, end in [
        ("temp", "2020-12-31T00:00:00+01:00"),
        ("other", "2021-12-31T00:00:00+01:00"),
    ]:
        create_manager_raw(
            {
                "user_key": f"manager-{person}",
                "manager_level": str(uuid4()),
                "manager_type": str(uuid4()),
                "responsibility": [],
                "org_unit": str(org_unit),
                "person": str(world[person]),
                "validity": {"from": "2020-01-01T00:00:00+01:00", "to": end},
            }
        )

    expected = {world[user_key] for user_key in expected}
    actual = read_employee_uuids(filter)
    assert actual == expected
