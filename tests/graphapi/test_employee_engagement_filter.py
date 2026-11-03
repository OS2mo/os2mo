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
        # Every employee with an engagement in the given org-unit
        (
            {"engagement": {"org_unit": {"user_keys": ["A"]}}},
            {"anna", "carl"},
        ),
        # Every employee with an engagement with the given job function
        (
            {"engagement": {"job_function": {"user_keys": ["tester"]}}},
            {"carl"},
        ),
        # Every employee with an engagement of the given engagement type
        (
            {"engagement": {"engagement_type": {"user_keys": ["temporary"]}}},
            {"bob", "carl"},
        ),
        # The engagement filter must be matched by a single engagement: carl is
        # engaged in A and as a developer, but not as a developer in A
        (
            {
                "engagement": {
                    "org_unit": {"user_keys": ["A"]},
                    "job_function": {"user_keys": ["developer"]},
                }
            },
            {"anna"},
        ),
        # An engagement can also be selected by its own user-key
        (
            {"engagement": {"user_keys": ["carl-B"]}},
            {"carl"},
        ),
        # The engagement filter can itself filter on employees: of anna and
        # dora, only anna has an engagement
        (
            {"engagement": {"employee": {"user_keys": ["anna", "dora"]}}},
            {"anna"},
        ),
        # Non-existent org-unit
        (
            {"engagement": {"org_unit": {"user_keys": ["does-not-exist"]}}},
            set(),
        ),
        # An empty engagement filter matches every employee that has any
        # engagement, so `dora`, whose only role is a managerial one, is never
        # returned
        (
            {"engagement": {}},
            {"anna", "bob", "carl"},
        ),
        # `null` is the inverse of `{}`: only employees without any engagement
        (
            {"engagement": None},
            {"dora"},
        ),
        # `null` AND's with the rest of the employee filter like any other
        # clause, so an employee that has an engagement is still excluded
        (
            {"engagement": None, "user_keys": ["anna"]},
            set(),
        ),
        (
            {"engagement": None, "user_keys": ["dora"]},
            {"dora"},
        ),
        # The engagement filter AND's with the rest of the employee filter
        (
            {
                "engagement": {"org_unit": {"user_keys": ["A"]}},
                "user_keys": ["carl"],
            },
            {"carl"},
        ),
        (
            {
                "engagement": {"org_unit": {"user_keys": ["A"]}},
                "user_keys": ["bob"],
            },
            set(),
        ),
    ],
)
def test_employee_engagement_filter(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[..., UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The employee `engagement` filter returns the employees behind the engagements.

    Engagements (employee -> org-unit, job function, engagement type):
        anna -> A, developer, permanent
        bob  -> B, developer, temporary
        carl -> A, tester, temporary
        carl -> B, developer, permanent
        dora -> (has no engagement, only a managerial role in A)
    """
    org_units = {
        "A": create_org_unit("A"),
        "B": create_org_unit("B"),
    }

    facets = {
        "engagement_job_function": create_facet(
            {"user_key": "engagement_job_function", "validity": {"from": "1970-01-01"}}
        ),
        "engagement_type": create_facet(
            {"user_key": "engagement_type", "validity": {"from": "1970-01-01"}}
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
            ("engagement_job_function", "developer"),
            ("engagement_job_function", "tester"),
            ("engagement_type", "permanent"),
            ("engagement_type", "temporary"),
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

    for person, org_unit, job_function, engagement_type in [
        ("anna", "A", "developer", "permanent"),
        ("bob", "B", "developer", "temporary"),
        ("carl", "A", "tester", "temporary"),
        ("carl", "B", "developer", "permanent"),
    ]:
        create_engagement(
            {
                "user_key": f"{person}-{org_unit}",
                "job_function": str(classes[job_function]),
                "engagement_type": str(classes[engagement_type]),
                "org_unit": str(org_units[org_unit]),
                "person": str(world[person]),
                "validity": {"from": "2020-01-01T00:00:00+01:00"},
            }
        )

    create_manager(org_units["A"], world["dora"])

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
            {"engagement": {"user_keys": ["engagement-temp"]}},
            set(),
        ),
        # Both the relation and the engagement org-function are dated back
        (
            {
                "engagement": {
                    "user_keys": ["engagement-temp"],
                    "from_date": "2020-06-01T00:00:00+01:00",
                },
                "from_date": "2020-06-01T00:00:00+01:00",
            },
            {"temp"},
        ),
        # Only the relation is dated back; the engagement org-function is not
        (
            {
                "engagement": {"user_keys": ["engagement-temp"]},
                "from_date": "2020-06-01T00:00:00+01:00",
            },
            set(),
        ),
        # Only the engagement org-function is dated back; the relation is not
        (
            {
                "engagement": {
                    "user_keys": ["engagement-temp"],
                    "from_date": "2020-06-01T00:00:00+01:00",
                }
            },
            set(),
        ),
        # Both outside the validity period
        (
            {
                "engagement": {
                    "user_keys": ["engagement-temp"],
                    "from_date": "2023-06-01T00:00:00+01:00",
                },
                "from_date": "2023-06-01T00:00:00+01:00",
            },
            set(),
        ),
        # `null` matches the employees without any engagement as of now, even
        # when the employee filter is dated back to when both were engaged
        (
            {"engagement": None, "from_date": "2020-06-01T00:00:00+01:00"},
            {"temp", "other"},
        ),
    ],
)
def test_employee_engagement_filter_respects_validity(
    read_employee_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """The engagement relation is only matched within its validity period.

    Engagements (employee -> user-key, validity):
        temp  -> engagement-temp,  2020-01-01 to 2020-12-31
        other -> engagement-other, 2020-01-01 to 2021-12-31

    `other` is unrelated to every non-`null` filter and must never show up in
    their results.
    """
    org_unit = create_org_unit("root")

    world = {
        "temp": create_person({"given_name": "Temp", "surname": "Employee"}),
        "other": create_person({"given_name": "Other", "surname": "Employee"}),
    }

    create_engagement(
        {
            "user_key": "engagement-temp",
            "job_function": str(uuid4()),
            "engagement_type": str(uuid4()),
            "org_unit": str(org_unit),
            "person": str(world["temp"]),
            "validity": {
                "from": "2020-01-01T00:00:00+01:00",
                "to": "2020-12-31T00:00:00+01:00",
            },
        }
    )
    create_engagement(
        {
            "user_key": "engagement-other",
            "job_function": str(uuid4()),
            "engagement_type": str(uuid4()),
            "org_unit": str(org_unit),
            "person": str(world["other"]),
            "validity": {
                "from": "2020-01-01T00:00:00+01:00",
                "to": "2021-12-31T00:00:00+01:00",
            },
        }
    )

    expected = {world[user_key] for user_key in expected}
    actual = read_employee_uuids(filter)
    assert actual == expected
