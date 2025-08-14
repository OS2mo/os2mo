# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.fixture
async def create_engagement(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        engagement_create_mutation = """
            mutation CreateEngagement($input: EngagementCreateInput!) {
                engagement_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(engagement_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        engagement_uuid = UUID(response.data["engagement_create"]["uuid"])
        return engagement_uuid

    return inner


@pytest.fixture
async def terminate_engagement(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        engagement_terminate_mutation = """
            mutation TerminateEngagement($input: EngagementTerminateInput!) {
                engagement_terminate(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(engagement_terminate_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        engagement_uuid = UUID(response.data["engagement_terminate"]["uuid"])
        return engagement_uuid

    return inner


@pytest.fixture
async def create_leave(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        leave_create_mutation = """
            mutation CreateLeave($input: LeaveCreateInput!) {
                leave_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(leave_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        leave_uuid = UUID(response.data["leave_create"]["uuid"])
        return leave_uuid

    return inner


@pytest.fixture
async def read_leave_engagement_uuid(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[UUID], UUID]:
    def inner(leave_uuid: UUID) -> UUID:
        leave_query = """
            query ReadLeaveEngagement($uuid: UUID!) {
              leaves(filter: { uuids: [$uuid] }) {
                objects {
                  validities {
                    engagement {
                      uuid
                    }
                  }
                }
              }
            }
        """
        response = graphapi_post(leave_query, {"uuid": str(leave_uuid)})
        assert response.errors is None
        assert response.data
        leave = one(response.data["leaves"]["objects"])
        return UUID(
            one({validity["engagement"]["uuid"] for validity in leave["validities"]})
        )

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_terminating_engagement_with_active_leave(
    create_person: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    terminate_engagement: Callable[[dict[str, Any]], UUID],
    create_leave: Callable[[dict[str, Any]], UUID],
    read_leave_engagement_uuid: Callable[[UUID], UUID],
) -> None:
    org_unit_uuid = create_org_unit("org_unit")

    person_uuid = create_person(
        {
            "given_name": "Xylia",
            "surname": "Shadowthorn",
        }
    )

    engagement_uuid = create_engagement(
        {
            "person": str(person_uuid),
            "org_unit": str(org_unit_uuid),
            "validity": {"from": "1970-01-01"},
            # Random uuids
            "engagement_type": "48151935-2f03-4ce0-a63f-7997bc81679c",
            "job_function": "c8119d43-d44c-42c7-82cd-b600100f6909",
        }
    )

    leave_uuid = create_leave(
        {
            "person": str(person_uuid),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2000-01-01"},
            # Random uuids
            "leave_type": "8fe816c5-acad-4d14-a440-b21576f1f54a",
        }
    )

    assert read_leave_engagement_uuid(leave_uuid) == engagement_uuid

    terminate_engagement({"uuid": str(engagement_uuid), "to": "1980-01-01"})

    with pytest.raises(AssertionError) as exc_info:
        read_leave_engagement_uuid(leave_uuid)
    assert "Cannot return null for non-nullable field Leave.engagement." in str(
        exc_info.value
    )
