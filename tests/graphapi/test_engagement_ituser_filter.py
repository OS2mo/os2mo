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
def read_engagement_user_keys(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[str]]:
    def inner(filter: dict[str, Any]) -> set[str]:
        response = graphapi_post(
            """
                query ReadEngagements($filter: EngagementFilter) {
                    engagements(filter: $filter) {
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
            for obj in response.data["engagements"]["objects"]
        }

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # Filter shape edge cases
        ({}, {"eng_a", "eng_b", "eng_in_two", "eng_orphan"}),
        ({"ituser": None}, {"eng_a", "eng_b", "eng_in_two", "eng_orphan"}),
        ({"ituser": {}}, {"eng_a", "eng_b", "eng_in_two"}),
        ({"ituser": {"uuids": []}}, set()),
        ({"ituser": {"user_keys": ["nonexistent"]}}, set()),
        # Single ituser → its engagement
        ({"ituser": {"user_keys": ["alpha"]}}, {"eng_a"}),
        ({"ituser": {"user_keys": ["beta"]}}, {"eng_b"}),
        ({"ituser": {"user_keys": ["gamma"]}}, {"eng_in_two"}),
        # OR semantics
        ({"ituser": {"user_keys": ["alpha", "gamma"]}}, {"eng_a", "eng_in_two"}),
        # Two itusers on the same engagement dedup
        ({"ituser": {"user_keys": ["beta", "beta2"]}}, {"eng_b"}),
        # ITUser without engagement_uuid matches nothing
        ({"ituser": {"user_keys": ["orphan"]}}, set()),
        ({"ituser": {"user_keys": ["alpha", "orphan"]}}, {"eng_a"}),
        # Nested ITUserFilter propagates
        (
            {"ituser": {"itsystem": {"user_keys": ["AD"]}}},
            {"eng_a", "eng_b", "eng_in_two"},
        ),
        # AND-combine with a sibling engagement filter
        (
            {
                "ituser": {"user_keys": ["alpha", "gamma"]},
                "org_unit": {"user_keys": ["ou1"]},
            },
            {"eng_a"},
        ),
        (
            {
                "ituser": {"user_keys": ["alpha"]},
                "org_unit": {"user_keys": ["ou2"]},
            },
            set(),
        ),
    ],
)
def test_engagement_ituser_filter(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    read_engagement_user_keys: Callable[[dict[str, Any]], set[str]],
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Filter engagements by ITUserFilter."""
    ad = create_itsystem(
        {"user_key": "AD", "name": "AD", "validity": {"from": "1970-01-01"}}
    )
    ou1 = create_org_unit("ou1")
    ou2 = create_org_unit("ou2")
    person = create_person()

    engagements: dict[str, UUID] = {}
    for user_key, org_unit in [
        ("eng_a", ou1),
        ("eng_b", ou1),
        ("eng_in_two", ou2),
        ("eng_orphan", ou1),
    ]:
        engagements[user_key] = create_engagement(
            {
                "user_key": user_key,
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "org_unit": str(org_unit),
                "person": str(person),
                "validity": {"from": "1970-01-01T00:00:00Z"},
            }
        )

    for user_key, engagement_user_key in [
        ("alpha", "eng_a"),
        ("beta", "eng_b"),
        ("beta2", "eng_b"),
        ("gamma", "eng_in_two"),
        ("orphan", None),
    ]:
        ituser_input: dict[str, Any] = {
            "user_key": user_key,
            "itsystem": str(ad),
            "person": str(person),
            "validity": {"from": "1970-01-01"},
        }
        if engagement_user_key is not None:
            ituser_input["engagement"] = str(engagements[engagement_user_key])
        create_ituser(ituser_input)

    assert read_engagement_user_keys(filter) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_engagement_filter_by_ituser_uuid(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    """Filtering by ituser UUID returns the engagement the ituser points at.

    Verifies the round-trip: an ITUser's `engagement_uuid` field agrees with
    what `engagements(filter: {ituser: {uuids: [ituser]}})` yields.
    """
    itsystem = create_itsystem(
        {"user_key": "AD", "name": "AD", "validity": {"from": "1970-01-01"}}
    )
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
    ituser = create_ituser(
        {
            "user_key": "u",
            "itsystem": str(itsystem),
            "person": str(person),
            "engagement": str(engagement),
            "validity": {"from": "1970-01-01"},
        }
    )

    response = graphapi_post(
        """
            query ReadITUser($uuid: UUID!) {
                itusers(filter: {uuids: [$uuid]}) {
                    objects {
                        current {
                            engagement_uuid
                        }
                    }
                }
            }
        """,
        variables={"uuid": str(ituser)},
    )
    assert response.errors is None
    assert response.data
    obj = one(response.data["itusers"]["objects"])
    assert obj["current"]["engagement_uuid"] == str(engagement)

    response = graphapi_post(
        """
            query ReadEngagements($filter: EngagementFilter) {
                engagements(filter: $filter) {
                    objects {
                        uuid
                    }
                }
            }
        """,
        variables={"filter": {"ituser": {"uuids": [str(ituser)]}}},
    )
    assert response.errors is None
    assert response.data
    assert {UUID(o["uuid"]) for o in response.data["engagements"]["objects"]} == {
        engagement
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_engagement_ituser_filter_no_leak_across_registrations(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    read_engagement_user_keys: Callable[[dict[str, Any]], set[str]],
) -> None:
    """An old ITUser registration must not leak engagement matches.

    Scenario:
      - ITUser X initially linked to engagement A.
      - ITUser X later updated to engagement B.
      - Filtering engagements by ITUser X must yield only {B}, never {A, B}.
    """
    itsystem = create_itsystem(
        {"user_key": "AD", "name": "AD", "validity": {"from": "1970-01-01"}}
    )
    ou = create_org_unit("ou")
    person = create_person()

    engagement_a = create_engagement(
        {
            "user_key": "eng_a",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou),
            "person": str(person),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )
    engagement_b = create_engagement(
        {
            "user_key": "eng_b",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(ou),
            "person": str(person),
            "validity": {"from": "1970-01-01T00:00:00Z"},
        }
    )

    ituser = create_ituser(
        {
            "user_key": "x",
            "itsystem": str(itsystem),
            "person": str(person),
            "engagement": str(engagement_a),
            "validity": {"from": "1970-01-01"},
        }
    )

    assert read_engagement_user_keys({"ituser": {"user_keys": ["x"]}}) == {"eng_a"}

    response = graphapi_post(
        """
            mutation UpdateITUser($input: ITUserUpdateInput!) {
                ituser_update(input: $input) {
                    uuid
                }
            }
        """,
        {
            "input": {
                "uuid": str(ituser),
                "engagement": str(engagement_b),
                "validity": {"from": "2000-01-01"},
            }
        },
    )
    assert response.errors is None

    assert read_engagement_user_keys({"ituser": {"user_keys": ["x"]}}) == {"eng_b"}
