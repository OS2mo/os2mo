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
def create_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID],
) -> Callable[..., UUID]:
    """Wrap the conftest create_engagement with defaults for this module."""

    def inner(
        org_unit: UUID,
        person: UUID,
        *,
        explicit_manager: UUID | None = None,
        job_function: UUID | None = None,
        primary: UUID | None = None,
        user_key: str | None = None,
    ) -> UUID:
        input: dict[str, Any] = {
            "org_unit": str(org_unit),
            "person": str(person),
            "engagement_type": str(uuid4()),
            "job_function": str(job_function or uuid4()),
            "validity": {"from": "2020-01-01", "to": None},
        }
        if explicit_manager is not None:
            input["explicit_manager"] = str(explicit_manager)
        if primary is not None:
            input["primary"] = str(primary)
        if user_key is not None:
            input["user_key"] = user_key
        return create_engagement(input)

    return inner


@pytest.fixture
def update_engagement(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], None]:
    def inner(input: dict[str, Any]) -> None:
        mutation = """
            mutation UpdateEngagement($input: EngagementUpdateInput!) {
                engagement_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(mutation, variables={"input": input})
        assert response.errors is None
        assert response.data

    return inner


@pytest.fixture
def read_engagement_uuids(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[UUID]]:
    def inner(filter: dict[str, Any]) -> set[UUID]:
        query = """
            query Engagements($filter: EngagementFilter!) {
                engagements(filter: $filter) {
                    objects { uuid }
                }
            }
        """
        response = graphapi_post(query, variables={"filter": filter})
        assert response.errors is None
        assert response.data
        return {UUID(o["uuid"]) for o in response.data["engagements"]["objects"]}

    return inner


@pytest.fixture
def read_explicit_manager(
    graphapi_post: GraphAPIPost,
) -> Callable[[UUID], UUID | None]:
    def inner(engagement_uuid: UUID) -> UUID | None:
        query = """
            query Engagement($uuid: UUID!) {
                engagements(filter: {uuids: [$uuid]}) {
                    objects {
                        current {
                            explicit_manager
                        }
                    }
                }
            }
        """
        response = graphapi_post(query, variables={"uuid": str(engagement_uuid)})
        assert response.errors is None
        assert response.data
        current = one(response.data["engagements"]["objects"])["current"]
        value = current["explicit_manager"]
        return UUID(value) if value else None

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "initial, update, expected",
    [
        # Set on an engagement without a manager
        (None, {"explicit_manager": "mgr_1"}, "mgr_1"),
        # Overwrite an existing manager
        ("mgr_1", {"explicit_manager": "mgr_2"}, "mgr_2"),
        # Omitting the field leaves the existing value untouched (PATCH)
        ("mgr_1", {}, "mgr_1"),
        # Explicit null clears the relation
        ("mgr_1", {"explicit_manager": None}, None),
        (None, {"explicit_manager": None}, None),
    ],
)
def test_engagement_explicit_manager(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    update_engagement: Callable[[dict[str, Any]], None],
    read_explicit_manager: Callable[[UUID], UUID | None],
    initial: str | None,
    update: dict[str, Any],
    expected: str | None,
) -> None:
    """Create with the given initial state, apply the update, check the result."""
    org_unit = create_org_unit("root")
    person = create_person()
    managers = {
        "mgr_1": create_manager(org_unit, person),
        "mgr_2": create_manager(org_unit, person),
    }

    engagement = create_engagement(
        org_unit, person, explicit_manager=managers.get(initial)
    )
    assert read_explicit_manager(engagement) == managers.get(initial)

    update_engagement(
        {
            "uuid": str(engagement),
            "validity": {"from": "2020-01-01", "to": None},
            **{k: str(managers[v]) if v in managers else v for k, v in update.items()},
        }
    )
    assert read_explicit_manager(engagement) == managers.get(expected)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter, expected_keys",
    [
        # Filter omitted returns everything
        ({}, {"e_a", "e_b", "e_none"}),
        # null returns only engagements without a manager
        ({"explicit_manager": None}, {"e_none"}),
        # Empty ManagerFilter returns engagements with any manager
        ({"explicit_manager": {}}, {"e_a", "e_b"}),
        # ManagerFilter narrows to engagements whose manager matches
        ({"explicit_manager": {"user_keys": ["mgr_a"]}}, {"e_a"}),
        # No match -> empty
        ({"explicit_manager": {"user_keys": ["unrelated"]}}, set()),
    ],
)
def test_engagement_explicit_manager_filter(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    read_engagement_uuids: Callable[[dict[str, Any]], set[UUID]],
    filter: dict[str, Any],
    expected_keys: set[str],
) -> None:
    """Three-state filter across engagements with and without managers."""
    org_unit = create_org_unit("root")
    person = create_person()
    mgr_a = create_manager(org_unit, person, user_key="mgr_a")
    mgr_b = create_manager(org_unit, person, user_key="mgr_b")

    engagements = {
        "e_a": create_engagement(org_unit, person, explicit_manager=mgr_a),
        "e_b": create_engagement(org_unit, person, explicit_manager=mgr_b),
        "e_none": create_engagement(org_unit, person),
    }

    assert read_engagement_uuids(filter) == {engagements[key] for key in expected_keys}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "update, expected",
    [
        # Update explicit_manager only -> other fields preserved.
        (
            {"explicit_manager": "mgr_2"},
            {
                "explicit_manager": "mgr_2",
                "job_function_uuid": "jf_1",
                "primary_uuid": "p_1",
                "user_key": "uk_1",
            },
        ),
        # Clear explicit_manager only -> other fields preserved.
        (
            {"explicit_manager": None},
            {
                "explicit_manager": None,
                "job_function_uuid": "jf_1",
                "primary_uuid": "p_1",
                "user_key": "uk_1",
            },
        ),
        # Update job_function only -> explicit_manager preserved.
        (
            {"job_function": "jf_2"},
            {
                "explicit_manager": "mgr_1",
                "job_function_uuid": "jf_2",
                "primary_uuid": "p_1",
                "user_key": "uk_1",
            },
        ),
    ],
)
def test_engagement_explicit_manager_does_not_affect_other_fields(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    create_itsystem: Callable[..., UUID],
    create_ituser: Callable[..., UUID],
    update_engagement: Callable[[dict[str, Any]], None],
    read_engagement_uuids: Callable[[dict[str, Any]], set[UUID]],
    update: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    """Partial updates only change the fields that were updated.

    Writing explicit_manager must preserve the engagement's other relations
    and attributes, and vice versa. An ITUser bound to the engagement (also
    a `tilknyttedefunktioner` relation, on the ITUser's own registration)
    must be unaffected throughout.
    """
    org_unit = create_org_unit("root")
    person = create_person()
    refs: dict[str, Any] = {
        "mgr_1": create_manager(org_unit, person),
        "mgr_2": create_manager(org_unit, person),
        "jf_1": uuid4(),
        "jf_2": uuid4(),
        "p_1": uuid4(),
        "uk_1": "uk_1",
    }
    engagement = create_engagement(
        org_unit,
        person,
        job_function=refs["jf_1"],
        primary=refs["p_1"],
        user_key="uk_1",
        explicit_manager=refs["mgr_1"],
    )
    itsystem = create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "2020-01-01"},
        }
    )
    ituser = create_ituser(
        {
            "user_key": "ad-account",
            "itsystem": str(itsystem),
            "person": str(person),
            "engagements": [str(engagement)],
            "validity": {"from": "2020-01-01", "to": None},
        }
    )

    def resolve(value: Any) -> Any:
        return str(refs[value]) if value in refs else value

    update_engagement(
        {
            "uuid": str(engagement),
            "validity": {"from": "2020-01-01", "to": None},
            **{k: resolve(v) for k, v in update.items()},
        }
    )

    # The engagement only changed in the updated fields
    read_query = """
        query Engagement($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        explicit_manager
                        job_function_uuid
                        primary_uuid
                        user_key
                    }
                }
            }
        }
    """
    response = graphapi_post(read_query, variables={"uuid": str(engagement)})
    assert response.errors is None
    assert response.data
    current = one(response.data["engagements"]["objects"])["current"]
    assert current == {k: resolve(v) for k, v in expected.items()}

    # The ITUser's binding to the engagement is unaffected
    ituser_query = """
        query ITUser($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        engagement_uuids
                    }
                }
            }
        }
    """
    response = graphapi_post(ituser_query, variables={"uuid": str(ituser)})
    assert response.errors is None
    assert response.data
    ituser_current = one(response.data["itusers"]["objects"])["current"]
    assert ituser_current["engagement_uuids"] == [str(engagement)]

    # ... and the engagement can still be found through it
    assert read_engagement_uuids({"ituser": {"uuids": [str(ituser)]}}) == {engagement}
