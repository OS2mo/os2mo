# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
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
