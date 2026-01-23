# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.fixture
def create_manager(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation CreateManager($input: ManagerCreateInput!) {
                manager_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_create"]["uuid"])

    return inner


@pytest.fixture
def update_manager(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateManager($input: ManagerUpdateInput!) {
                manager_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_update"]["uuid"])

    return inner


@pytest.fixture
def read_manager_engagement(
    graphapi_post: GraphAPIPost,
) -> Callable[[UUID], UUID | None]:
    def inner(manager_uuid: UUID) -> UUID | None:
        query = """
        query ReadManager($uuid: [UUID!]) {
          managers(filter: { uuids: $uuid }) {
            objects {
              current {
                engagement_response {
                  uuid
                }
              }
            }
          }
        }
        """
        response = graphapi_post(query, variables={"uuid": [str(manager_uuid)]})
        assert response.errors is None
        assert response.data
        manager = one(response.data["managers"]["objects"])
        engagement = manager["current"]["engagement_response"]
        if engagement is None:
            return None
        return UUID(engagement["uuid"])

    return inner


@pytest.fixture
def manager_structure(
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> dict[str, Any]:
    org_unit_uuid = create_org_unit("unit", None)
    person_uuid = create_person(None)

    # manager_type
    manager_type_facet = create_facet(
        {"user_key": "manager_type", "validity": {"from": "1900-01-01"}}
    )
    manager_type = create_class(
        {
            "facet_uuid": str(manager_type_facet),
            "user_key": "manager_type_1",
            "name": "Manager Type 1",
            "validity": {"from": "1900-01-01"},
        }
    )

    # manager_level
    manager_level_facet = create_facet(
        {"user_key": "manager_level", "validity": {"from": "1900-01-01"}}
    )
    manager_level = create_class(
        {
            "facet_uuid": str(manager_level_facet),
            "user_key": "manager_level_1",
            "name": "Manager Level 1",
            "validity": {"from": "1900-01-01"},
        }
    )

    # engagement_type
    engagement_type_facet = create_facet(
        {"user_key": "engagement_type", "validity": {"from": "1900-01-01"}}
    )
    engagement_type = create_class(
        {
            "facet_uuid": str(engagement_type_facet),
            "user_key": "engagement_type_1",
            "name": "Engagement Type 1",
            "validity": {"from": "1900-01-01"},
        }
    )

    # job_function
    job_function_facet = create_facet(
        {"user_key": "job_function", "validity": {"from": "1900-01-01"}}
    )
    job_function = create_class(
        {
            "facet_uuid": str(job_function_facet),
            "user_key": "job_function_1",
            "name": "Job Function 1",
            "validity": {"from": "1900-01-01"},
        }
    )

    return {
        "org_unit_uuid": org_unit_uuid,
        "person_uuid": person_uuid,
        "manager_type": manager_type,
        "manager_level": manager_level,
        "engagement_type": engagement_type,
        "job_function": job_function,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_create_manager_with_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[[dict[str, Any]], UUID],
    read_manager_engagement: Callable[[UUID], UUID | None],
    manager_structure: dict[str, Any],
) -> None:
    org_unit_uuid = manager_structure["org_unit_uuid"]
    person_uuid = manager_structure["person_uuid"]
    manager_type = manager_structure["manager_type"]
    manager_level = manager_structure["manager_level"]
    engagement_type = manager_structure["engagement_type"]
    job_function = manager_structure["job_function"]

    engagement_uuid = create_engagement(
        {
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "engagement_type": str(engagement_type),
            "job_function": str(job_function),
            "validity": {"from": "2020-01-01"},
        }
    )

    # Create a manager WITH engagement
    manager_uuid = create_manager(
        {
            "person": str(person_uuid),
            "responsibility": [],
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert read_manager_engagement(manager_uuid) == engagement_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_update_manager_add_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[[dict[str, Any]], UUID],
    update_manager: Callable[[dict[str, Any]], UUID],
    read_manager_engagement: Callable[[UUID], UUID | None],
    manager_structure: dict[str, Any],
) -> None:
    org_unit_uuid = manager_structure["org_unit_uuid"]
    person_uuid = manager_structure["person_uuid"]
    manager_type = manager_structure["manager_type"]
    manager_level = manager_structure["manager_level"]
    engagement_type = manager_structure["engagement_type"]
    job_function = manager_structure["job_function"]

    engagement_uuid = create_engagement(
        {
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "engagement_type": str(engagement_type),
            "job_function": str(job_function),
            "validity": {"from": "2020-01-01"},
        }
    )

    # Create a manager WITHOUT engagement
    manager_uuid = create_manager(
        {
            "person": str(person_uuid),
            "responsibility": [],
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert read_manager_engagement(manager_uuid) is None

    # Update the manager to ADD the engagement
    update_manager(
        {
            "uuid": str(manager_uuid),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2020-01-01"},
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
        }
    )
    assert read_manager_engagement(manager_uuid) == engagement_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_update_manager_explicit_none_clears_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[[dict[str, Any]], UUID],
    update_manager: Callable[[dict[str, Any]], UUID],
    read_manager_engagement: Callable[[UUID], UUID | None],
    manager_structure: dict[str, Any],
) -> None:
    org_unit_uuid = manager_structure["org_unit_uuid"]
    person_uuid = manager_structure["person_uuid"]
    manager_type = manager_structure["manager_type"]
    manager_level = manager_structure["manager_level"]
    engagement_type = manager_structure["engagement_type"]
    job_function = manager_structure["job_function"]

    engagement_uuid = create_engagement(
        {
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "engagement_type": str(engagement_type),
            "job_function": str(job_function),
            "validity": {"from": "2020-01-01"},
        }
    )

    # Create a manager WITH engagement
    manager_uuid = create_manager(
        {
            "person": str(person_uuid),
            "responsibility": [],
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert read_manager_engagement(manager_uuid) == engagement_uuid

    # Update the manager REMOVE the engagement
    update_manager(
        {
            "uuid": str(manager_uuid),
            "engagement": None,
            "validity": {"from": "2020-02-01"},
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
        }
    )
    assert read_manager_engagement(manager_uuid) is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_update_manager_partial_update_clears_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_manager: Callable[[dict[str, Any]], UUID],
    update_manager: Callable[[dict[str, Any]], UUID],
    read_manager_engagement: Callable[[UUID], UUID | None],
    manager_structure: dict[str, Any],
) -> None:
    org_unit_uuid = manager_structure["org_unit_uuid"]
    person_uuid = manager_structure["person_uuid"]
    manager_type = manager_structure["manager_type"]
    manager_level = manager_structure["manager_level"]
    engagement_type = manager_structure["engagement_type"]
    job_function = manager_structure["job_function"]

    engagement_uuid = create_engagement(
        {
            "org_unit": str(org_unit_uuid),
            "person": str(person_uuid),
            "engagement_type": str(engagement_type),
            "job_function": str(job_function),
            "validity": {"from": "2020-01-01"},
        }
    )

    # Create a manager WITH engagement
    manager_uuid = create_manager(
        {
            "person": str(person_uuid),
            "responsibility": [],
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
            "engagement": str(engagement_uuid),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert read_manager_engagement(manager_uuid) == engagement_uuid

    # Update the manager WITHOUT providing engagement
    # With PATCH semantics this would leave the engagement relation alone
    # However with PUT semantics this clears the engagement field
    # We currently have PUT semantics, so the field is cleared
    update_manager(
        {
            "uuid": str(manager_uuid),
            # engagement is omitted here
            "validity": {"from": "2020-02-01"},
            "org_unit": str(org_unit_uuid),
            "manager_type": str(manager_type),
            "manager_level": str(manager_level),
        }
    )
    assert read_manager_engagement(manager_uuid) is None
