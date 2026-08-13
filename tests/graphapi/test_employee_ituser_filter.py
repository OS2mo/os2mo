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
        # Every employee with an IT-user in the given IT-system
        (
            {"ituser": {"itsystem": {"user_keys": ["AD"]}}},
            {"anna", "bob"},
        ),
        (
            {"ituser": {"itsystem": {"user_keys": ["LDAP"]}}},
            {"carl"},
        ),
        # IT-system plus external ID: exactly the one matching employee
        # This is the shape the PBAC owner rules use
        (
            {"ituser": {"itsystem": {"user_keys": ["AD"]}, "external_ids": ["abc"]}},
            {"anna"},
        ),
        # The same external ID exists in both IT-systems, so without an
        # IT-system both employees are returned
        (
            {"ituser": {"external_ids": ["abc"]}},
            {"anna", "carl"},
        ),
        # `external_ids` is OR'ed within the IT-system
        (
            {
                "ituser": {
                    "itsystem": {"user_keys": ["AD"]},
                    "external_ids": ["abc", "xyz"],
                }
            },
            {"anna", "bob"},
        ),
        # An IT-user can also be selected by its own user-key
        (
            {"ituser": {"user_keys": ["ituser-anna"]}},
            {"anna"},
        ),
        # Non-existent external ID and IT-system
        (
            {"ituser": {"external_ids": ["does-not-exist"]}},
            set(),
        ),
        (
            {"ituser": {"itsystem": {"user_keys": ["does-not-exist"]}}},
            set(),
        ),
        # An empty IT-user filter matches every employee that has any IT-user,
        # so `dora`, who has none, is never returned
        (
            {"ituser": {}},
            {"anna", "bob", "carl"},
        ),
        # `null` is the inverse of `{}`: only employees without any IT-user
        (
            {"ituser": None},
            {"dora"},
        ),
        # `null` AND's with the rest of the employee filter like any other
        # clause, so an employee that has an IT-user is still excluded
        (
            {"ituser": None, "user_keys": ["anna"]},
            set(),
        ),
        (
            {"ituser": None, "user_keys": ["dora"]},
            {"dora"},
        ),
        # The IT-user filter AND's with the rest of the employee filter
        (
            {
                "ituser": {"itsystem": {"user_keys": ["AD"]}},
                "user_keys": ["anna"],
            },
            {"anna"},
        ),
        (
            {
                "ituser": {"itsystem": {"user_keys": ["AD"]}},
                "user_keys": ["carl"],
            },
            set(),
        ),
    ],
)
def test_employee_ituser_filter(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The employee `ituser` filter returns the employees behind the IT-users.

    IT-user graph (employee -> IT-system, external ID):
        anna -> AD, abc
        bob  -> AD, xyz
        carl -> LDAP, abc
        dora -> (has no IT-user)
    """
    itsystems = {
        user_key: create_itsystem(
            {
                "user_key": user_key,
                "name": user_key,
                "validity": {"from": "1970-01-01"},
            }
        )
        for user_key in ["AD", "LDAP"]
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

    for person, itsystem, external_id in [
        ("anna", "AD", "abc"),
        ("bob", "AD", "xyz"),
        ("carl", "LDAP", "abc"),
    ]:
        create_ituser(
            {
                "user_key": f"ituser-{person}",
                "external_id": external_id,
                "itsystem": str(itsystems[itsystem]),
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
        # By default the filter is evaluated as of now, where both have expired
        (
            {"ituser": {"external_ids": ["temp-ext"]}},
            set(),
        ),
        # Both the relation and the IT-user org-function are dated back
        (
            {
                "ituser": {
                    "external_ids": ["temp-ext"],
                    "from_date": "2020-06-01T00:00:00+01:00",
                },
                "from_date": "2020-06-01T00:00:00+01:00",
            },
            {"temp"},
        ),
        # Only the relation is dated back; the IT-user org-function is not
        (
            {
                "ituser": {"external_ids": ["temp-ext"]},
                "from_date": "2020-06-01T00:00:00+01:00",
            },
            set(),
        ),
        # Only the IT-user org-function is dated back; the relation is not
        (
            {
                "ituser": {
                    "external_ids": ["temp-ext"],
                    "from_date": "2020-06-01T00:00:00+01:00",
                }
            },
            set(),
        ),
        # Both outside the validity period
        (
            {
                "ituser": {
                    "external_ids": ["temp-ext"],
                    "from_date": "2023-06-01T00:00:00+01:00",
                },
                "from_date": "2023-06-01T00:00:00+01:00",
            },
            set(),
        ),
        # `null` inherits the employee filter's validity: temp's IT-user has
        # expired by 2021, while other's is still active
        (
            {"ituser": None, "from_date": "2021-06-01T00:00:00+01:00"},
            {"temp"},
        ),
        # Back when both IT-users were active, nobody is without one
        (
            {"ituser": None, "from_date": "2020-06-01T00:00:00+01:00"},
            set(),
        ),
    ],
)
def test_employee_ituser_filter_respects_validity(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The IT-user relation is only matched within its validity period.

    IT-user graph (employee -> external ID, validity):
        temp  -> temp-ext,  2020-01-01 to 2020-12-31
        other -> other-ext, 2020-01-01 to 2021-12-31

    `other` is unrelated to every filter and must never show up in the result.
    """
    itsystem = create_itsystem(
        {"user_key": "AD", "name": "AD", "validity": {"from": "1970-01-01"}}
    )

    world = {
        "temp": create_person({"given_name": "Temp", "surname": "Employee"}),
        "other": create_person({"given_name": "Other", "surname": "Employee"}),
    }

    for person, end in [
        ("temp", "2020-12-31T00:00:00+01:00"),
        ("other", "2021-12-31T00:00:00+01:00"),
    ]:
        create_ituser(
            {
                "user_key": f"ituser-{person}",
                "external_id": f"{person}-ext",
                "itsystem": str(itsystem),
                "person": str(world[person]),
                "validity": {"from": "2020-01-01T00:00:00+01:00", "to": end},
            }
        )

    expected = {world[user_key] for user_key in expected}
    actual = read_employee_uuids(filter)
    assert actual == expected
