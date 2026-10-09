# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost

MANAGER_UUID1 = UUID("00000000-0000-0000-0000-000000000001")
MANAGER_UUID2 = UUID("00000000-0000-0000-0000-000000000002")
JOB_FUNCTION_UUID1 = UUID("00000000-0000-0000-0000-000000000003")
JOB_FUNCTION_UUID2 = UUID("00000000-0000-0000-0000-000000000004")


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
                            explicit_manager {
                                uuid
                            }
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
        return UUID(value["uuid"]) if value else None

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "initial_manager_uuid, update, expected_manager_uuid",
    [
        # Set on an engagement without a manager
        (None, {"explicit_manager": str(MANAGER_UUID1)}, MANAGER_UUID1),
        # Overwrite an existing manager
        (MANAGER_UUID1, {"explicit_manager": str(MANAGER_UUID2)}, MANAGER_UUID2),
        # Omitting the field leaves the existing value untouched (PATCH)
        (MANAGER_UUID1, {}, MANAGER_UUID1),
        # Explicit null clears the relation
        (MANAGER_UUID1, {"explicit_manager": None}, None),
        (None, {"explicit_manager": None}, None),
    ],
)
def test_engagement_explicit_manager(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[..., UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    read_explicit_manager: Callable[[UUID], UUID | None],
    initial_manager_uuid: UUID | None,
    update: dict[str, Any],
    expected_manager_uuid: UUID | None,
) -> None:
    """Create with the given initial state, apply the update, check the result."""
    # Arrange
    org_unit = create_org_unit("root")
    person = create_person()
    create_manager(org_unit, person, uuid=MANAGER_UUID1)
    create_manager(org_unit, person, uuid=MANAGER_UUID2)
    engagement_data: dict[str, Any] = {
        "org_unit": str(org_unit),
        "person": str(person),
        "engagement_type": str(uuid4()),
        "job_function": str(uuid4()),
        "validity": {"from": "2020-01-01", "to": None},
    }
    if initial_manager_uuid is not None:
        engagement_data["explicit_manager"] = str(initial_manager_uuid)
    engagement_uuid = create_engagement(engagement_data)

    # Act
    update_engagement(
        {
            "uuid": str(engagement_uuid),
            "validity": {"from": "2020-01-01", "to": None},
            **update,
        }
    )

    # Assert
    assert read_explicit_manager(engagement_uuid) == expected_manager_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter, expected_engagements",
    [
        # Filter omitted returns everything
        ({}, {"eng_manager1", "eng_manager2", "eng_no_manager"}),
        # null returns only engagements without a manager
        ({"explicit_manager": None}, {"eng_no_manager"}),
        # Empty ManagerFilter returns engagements with any manager
        ({"explicit_manager": {}}, {"eng_manager1", "eng_manager2"}),
        # ManagerFilter narrows to engagements whose manager matches
        ({"explicit_manager": {"user_keys": ["manager1"]}}, {"eng_manager1"}),
        # No match -> empty
        ({"explicit_manager": {"user_keys": ["unrelated"]}}, set()),
    ],
)
def test_engagement_explicit_manager_filter(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[..., UUID],
    read_engagement_uuids: Callable[[dict[str, Any]], set[UUID]],
    filter: dict[str, Any],
    expected_engagements: set[str],
) -> None:
    """Three-state filter across engagements with and without managers."""
    # Arrange
    org_unit = create_org_unit("root")
    person = create_person()
    manager1 = create_manager(org_unit, person, user_key="manager1")
    manager2 = create_manager(org_unit, person, user_key="manager2")
    engagement_data = {
        "org_unit": str(org_unit),
        "person": str(person),
        "engagement_type": str(uuid4()),
        "job_function": str(uuid4()),
        "validity": {"from": "2020-01-01", "to": None},
    }
    engagements = {
        "eng_manager1": create_engagement(
            {**engagement_data, "explicit_manager": str(manager1)}
        ),
        "eng_manager2": create_engagement(
            {**engagement_data, "explicit_manager": str(manager2)}
        ),
        "eng_no_manager": create_engagement(engagement_data),
    }

    # Act
    result = read_engagement_uuids(filter)

    # Assert
    assert result == {engagements[key] for key in expected_engagements}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "update, expected",
    [
        # Update explicit_manager only -> other fields preserved.
        (
            {"explicit_manager": str(MANAGER_UUID2)},
            {
                "explicit_manager": {"uuid": str(MANAGER_UUID2)},
                "job_function_uuid": str(JOB_FUNCTION_UUID1),
            },
        ),
        # Clear explicit_manager only -> other fields preserved.
        (
            {"explicit_manager": None},
            {
                "explicit_manager": None,
                "job_function_uuid": str(JOB_FUNCTION_UUID1),
            },
        ),
        # Update job_function only -> explicit_manager preserved.
        (
            {"job_function": str(JOB_FUNCTION_UUID2)},
            {
                "explicit_manager": {"uuid": str(MANAGER_UUID1)},
                "job_function_uuid": str(JOB_FUNCTION_UUID2),
            },
        ),
    ],
)
def test_engagement_explicit_manager_does_not_affect_other_fields(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[..., UUID],
    create_itsystem: Callable[..., UUID],
    create_ituser: Callable[..., UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    read_engagement_uuids: Callable[[dict[str, Any]], set[UUID]],
    update: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    """
    Partial updates only change the fields that were updated.

    Writing explicit_manager must preserve the engagement's other relations
    and attributes.
    """
    # Arrange
    primary_uuid = uuid4()
    engagement_user_key = "12345"

    org_unit = create_org_unit("root")
    person = create_person()
    create_manager(org_unit, person, uuid=MANAGER_UUID1)
    create_manager(org_unit, person, uuid=MANAGER_UUID2)

    engagement_uuid = create_engagement(
        {
            "org_unit": str(org_unit),
            "person": str(person),
            "engagement_type": str(uuid4()),
            "job_function": str(JOB_FUNCTION_UUID1),
            "primary": str(primary_uuid),
            "user_key": engagement_user_key,
            "explicit_manager": str(MANAGER_UUID1),
            "validity": {"from": "2020-01-01", "to": None},
        }
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
            "engagements": [str(engagement_uuid)],
            "validity": {"from": "2020-01-01", "to": None},
        }
    )

    # Act
    update_engagement(
        {
            "uuid": str(engagement_uuid),
            "validity": {"from": "2020-01-01", "to": None},
            **update,
        }
    )

    # Assert
    # The engagement only changed in the updated fields
    get_engagement_query = """
        query Engagement($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        explicit_manager {
                            uuid
                        }
                        job_function_uuid
                        primary_uuid
                        user_key
                    }
                }
            }
        }
    """
    eng_response = graphapi_post(
        get_engagement_query, variables={"uuid": str(engagement_uuid)}
    )
    assert eng_response.errors is None
    assert eng_response.data
    current = one(eng_response.data["engagements"]["objects"])["current"]

    assert current == {
        **expected,
        "primary_uuid": str(primary_uuid),
        "user_key": engagement_user_key,
    }

    # The ITUser's binding to the engagement is unaffected
    assert read_engagement_uuids({"ituser": {"uuids": [str(ituser)]}}) == {
        engagement_uuid
    }
