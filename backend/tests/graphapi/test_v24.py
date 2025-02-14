# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

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


@pytest.fixture
def update_manager(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[UUID, UUID | None], UUID]:
    def inner(manager_uuid: UUID, person: UUID | None = None) -> UUID:
        mutate_query = """
            mutation UpdateManager($input: ManagerUpdateInput!) {
                manager_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "uuid": str(manager_uuid),
                    "person": str(person) if person else None,
                    "validity": {"from": "1980-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_update"]["uuid"])

    return inner


@pytest.fixture
def fetch_managers(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any] | None], set[UUID]]:
    def inner(filter: dict[str, Any] | None) -> set[UUID]:
        # Test our filter
        query = """
            query Managers($filter: ManagerFilter) {
              managers(filter: $filter) {
                objects {
                  uuid
                }
              }
            }
        """
        response = graphapi_post(
            query, variables={"filter": filter}, url="/graphql/v24"
        )
        assert response.errors is None
        assert response.data
        return {
            UUID(manager["uuid"]) for manager in response.data["managers"]["objects"]
        }

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expect_manager,expect_vacant",
    [
        # No filter fetches all
        (None, True, True),
        # Employee wildcard filters vacant
        ({"employee": {}}, True, False),
        # Employee none filters nothing, fetches all
        ({"employee": None}, True, True),
    ],
)
async def test_vacant_manager(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    fetch_managers: Callable[..., UUID],
    filter: dict[str, Any] | None,
    expect_manager: bool,
    expect_vacant: bool,
) -> None:
    """Test that the we can find vacant managers using GraphQL.

    Args:
        graphapi_post: The GraphQL client to run our query with.
        create_org_unit: Helper to create organisation units.
        create_person: Helper to create people.
        create_manager: Helper to create managers.
        fetch_managers: Helper to fetch managers.
        filter: The filter to apply to fetch managers.
        expect_manager: Whether to the expect the manager in the output.
        expect_vacant: Whether to the expect the vacant manager in the output.
    """
    root1 = create_org_unit("root1")
    root2 = create_org_unit("root2")
    # Create an occupied manager
    person = create_person()
    manager = create_manager(root1, person)
    # Create a vacant manager
    vacant = create_manager(root2)

    expected = set()
    if expect_manager:
        expected.add(manager)
    if expect_vacant:
        expected.add(vacant)

    result = fetch_managers(filter)
    assert result == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_vacant_manager_change_vacate(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    update_manager: Callable[..., UUID],
    fetch_managers: Callable[..., UUID],
) -> None:
    """Test that the we can find vacant managers using GraphQL.

    Args:
        graphapi_post: The GraphQL client to run our query with.
        create_org_unit: Helper to create organisation units.
        create_person: Helper to create people.
        create_manager: Helper to create managers.
        update_manager: Helper to edit managers.
        fetch_managers: Helper to fetch managers.
    """
    root1 = create_org_unit("root1")
    person = create_person()
    manager = create_manager(root1, person)

    # Employee none filters nothing, fetches all
    result = fetch_managers({"employee": None})
    assert result == {manager}

    # Unoccupy the manager
    update_manager(manager)

    # Employee none filters nothing, fetches all
    result = fetch_managers({"employee": None})
    assert result == {manager}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_vacant_manager_change_occupy(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    update_manager: Callable[..., UUID],
    fetch_managers: Callable[..., UUID],
) -> None:
    """Test that the we can find vacant managers using GraphQL.

    Args:
        graphapi_post: The GraphQL client to run our query with.
        create_org_unit: Helper to create organisation units.
        create_person: Helper to create people.
        create_manager: Helper to create managers.
        update_manager: Helper to edit managers.
        fetch_managers: Helper to fetch managers.
    """
    root1 = create_org_unit("root1")
    person = create_person()
    manager = create_manager(root1)

    # Employee none filters nothing, fetches all
    result = fetch_managers({"employee": None})
    assert result == {manager}

    # Unoccupy the manager
    update_manager(manager, person)

    # Employee none filters nothing, fetches all
    result = fetch_managers({"employee": None})
    assert result == {manager}
