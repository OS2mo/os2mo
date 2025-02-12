# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import only

from ..conftest import GraphAPIPost


@pytest.fixture
def root_org(graphapi_post: GraphAPIPost) -> UUID:
    mutate_query = """
        mutation CreateOrg($input: OrganisationCreate!) {
            org_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        query=mutate_query, variables={"input": {"municipality_code": None}}
    )
    assert response.errors is None
    assert response.data
    return UUID(response.data["org_create"]["uuid"])


@pytest.fixture
def create_org_unit(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[str, UUID | None], UUID]:
    def inner(user_key: str, parent: UUID | None = None) -> UUID:
        mutate_query = """
            mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "name": user_key,
                    "user_key": user_key,
                    "parent": str(parent) if parent else None,
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                    "org_unit_type": str(uuid4()),
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_create"]["uuid"])

    return inner


@pytest.fixture
def create_person(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[], UUID]:
    def inner() -> UUID:
        mutate_query = """
            mutation CreatePerson($input: EmployeeCreateInput!) {
                employee_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "given_name": str(uuid4()),
                    "surname": str(uuid4()),
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["employee_create"]["uuid"])

    return inner


@pytest.fixture
def create_engagement(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[UUID, UUID], UUID]:
    def inner(
        org_unit: UUID,
        person: UUID,
    ) -> UUID:
        mutate_query = """
            mutation CreateEngagement($input: EngagementCreateInput!) {
                engagement_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "engagement_type": str(uuid4()),
                    "job_function": str(uuid4()),
                    "org_unit": str(org_unit),
                    "person": str(person),
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["engagement_create"]["uuid"])

    return inner


@pytest.fixture
def create_manager(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[UUID, UUID | None], UUID]:
    def inner(org_unit: UUID, person: UUID | None = None) -> UUID:
        mutate_query = """
            mutation CreateManager($input: ManagerCreateInput!) {
                manager_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "manager_level": str(uuid4()),
                    "manager_type": str(uuid4()),
                    "responsibility": [],
                    "org_unit": str(org_unit),
                    "person": str(person) if person else None,
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_create"]["uuid"])

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "inherit,exclude_self,expected",
    [
        (False, False, "ll"),
        # We would find ourselves, but we are excluded, so we find nothing
        (False, True, None),
        # We could inherit, but we do not need to as we find ourselves
        (True, False, "ll"),
        # We exclude ourselves in two layers, and then find the root manager
        (True, True, "root"),
    ],
)
async def test_exclude_self(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_engagement: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    inherit: bool,
    exclude_self: bool,
    expected: str | None,
) -> None:
    """Test that the exclude-self flag on engagement.managers work as expected.

    Args:
        graphapi_post: The GraphQL client to run our query with.
        create_org_unit: Helper to create organisation units.
        create_person: Helper to create people.
        create_engagement: Helper to create engagements.
        create_manager: Helper to create managers.
        inherit: Whether to inherit managers.
        exclude_self: Whether to exclude self in manager lookup.
        expected: The expected manager to get back.
    """

    # Construct our test-tree
    #     root
    #     /
    #    l
    #   /
    # ll
    root = create_org_unit("root")
    left = create_org_unit("l", root)
    ll = create_org_unit("ll", left)

    # Add root manager to the root node
    root_person = create_person()
    root_manager = create_manager(root, root_person)

    # Add our own person as manager for both l and ll
    person = create_person()
    create_manager(left, person)
    ll_manager = create_manager(ll, person)

    # Add our own person with engagement on ll
    ll_engagement = create_engagement(ll, person)

    # Test our filter
    query = """
        query ExcludeSelf(
          $filter: EngagementFilter!,
          $inherit: Boolean!
          $exclude_self: Boolean!
        ) {
          engagements(filter: $filter) {
            objects {
              current {
                managers(inherit: $inherit, exclude_self: $exclude_self) {
                    uuid
                }
              }
            }
          }
        }
    """
    response = graphapi_post(
        query,
        variables={
            "filter": {"uuids": [str(ll_engagement)]},
            "inherit": inherit,
            "exclude_self": exclude_self,
        },
    )
    assert response.errors is None
    assert response.data
    result = only(
        [
            UUID(manager["uuid"])
            for engagement in response.data["engagements"]["objects"]
            for manager in engagement["current"]["managers"]
            if engagement["current"] is not None
        ]
    )
    if expected is None:
        assert result is None
    if expected == "root":
        assert result == root_manager
    if expected == "ll":
        assert result == ll_manager
