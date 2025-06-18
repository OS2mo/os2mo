# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from ..conftest import GraphAPIPost


@pytest.fixture
def create_org(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        org_create_mutation = """
            mutation CreateOrganisation($input: OrganisationCreate!) {
                org_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(org_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        org_uuid = response.data["org_create"]["uuid"]
        return org_uuid

    return inner


@pytest.fixture
def root_org(create_org: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_org({"municipality_code": None})


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
def create_facet(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        facet_create_mutation = """
            mutation CreateFacet($input: FacetCreateInput!) {
                facet_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(facet_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return response.data["facet_create"]["uuid"]

    return inner


@pytest.fixture
def role_facet(create_facet: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_facet(
        {
            "user_key": "role",
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def create_itsystem(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        itsystem_create_mutation = """
            mutation CreateITSystem($input: ITSystemCreateInput!) {
                itsystem_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(itsystem_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        itsystem_uuid = UUID(response.data["itsystem_create"]["uuid"])
        return itsystem_uuid

    return inner


@pytest.fixture
def create_class(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        class_create_mutation = """
            mutation CreateRole($input: ClassCreateInput!) {
                class_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(class_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        class_uuid = UUID(response.data["class_create"]["uuid"])
        return class_uuid

    return inner
