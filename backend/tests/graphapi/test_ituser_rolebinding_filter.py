# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.fixture
def read_facet_uuid(graphapi_post: GraphAPIPost) -> Callable[[str], UUID]:
    def inner(user_key: str) -> UUID:
        facet_uuid_query = """
            query ReadFacetUUID($user_key: String!) {
                facets(filter: {user_keys: [$user_key]}) {
                    objects {
                        uuid
                    }
                }
            }
        """
        response = graphapi_post(facet_uuid_query, {"user_key": user_key})
        assert response.errors is None
        assert response.data
        facet_uuid = one(response.data["facets"]["objects"])["uuid"]
        return facet_uuid

    return inner


@pytest.fixture
def create_itsystem(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
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
def create_class(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
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


@pytest.fixture
def create_ituser(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        ituser_create_mutation = """
            mutation ITUserCreate($input: ITUserCreateInput!) {
                ituser_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(ituser_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        ituser_uuid = UUID(response.data["ituser_create"]["uuid"])
        return ituser_uuid

    return inner


@pytest.fixture
def create_person(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        person_create_mutation = """
            mutation PersonCreate($input: EmployeeCreateInput!) {
                employee_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(person_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        person_uuid = UUID(response.data["employee_create"]["uuid"])
        return person_uuid

    return inner


@pytest.fixture
def create_rolebinding(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        rolebinding_create_mutation = """
            mutation RoleBindingCreate($input: RoleBindingCreateInput!) {
                rolebinding_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(rolebinding_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        rolebinding_uuid = UUID(response.data["rolebinding_create"]["uuid"])
        return rolebinding_uuid

    return inner


@pytest.fixture
def read_ituser_uuids(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[UUID]]:
    def inner(filter: dict[str, Any]) -> set[UUID]:
        ituser_uuid_query = """
            query ReadITUsers($filter: ITUserFilter) {
                itusers(filter: $filter) {
                    objects {
                        uuid
                    }
                }
            }
        """
        response = graphapi_post(ituser_uuid_query, {"filter": filter})
        assert response.errors is None
        assert response.data
        return {UUID(obj["uuid"]) for obj in response.data["itusers"]["objects"]}

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_ituser_rolebinding_filter(
    read_facet_uuid: Callable[[str], UUID],
    read_ituser_uuids: Callable[[dict[str, Any]], set[UUID]],
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
) -> None:
    """Test that we can filter by rolebindings on itusers."""
    # Create new itsystem
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "2024-01-01"},
        }
    )

    # Create a rolebinding role
    role_facet_uuid = read_facet_uuid("role")
    admin_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet_uuid),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    reader_class_uuid = create_class(
        {
            "user_key": "reader",
            "name": "Read-only",
            "facet_uuid": str(role_facet_uuid),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    result = read_ituser_uuids(
        {
            "itsystem": {"uuids": [str(itsystem_uuid)]},
        }
    )
    assert result == set()

    person_uuid = create_person(
        {
            "given_name": "Xylia",
            "surname": "Shadowthorn",
        }
    )

    ituser_uuid = create_ituser(
        {
            "user_key": "xylia",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    result = read_ituser_uuids(
        {
            "itsystem": {"uuids": [str(itsystem_uuid)]},
        }
    )
    assert result == {ituser_uuid}

    result = read_ituser_uuids(
        {
            "itsystem": {"uuids": [str(itsystem_uuid)]},
            "rolebinding": None,
        }
    )
    assert result == {ituser_uuid}

    rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_admin",
            "ituser": str(ituser_uuid),
            "role": str(admin_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    result = read_ituser_uuids(
        {
            "itsystem": {"uuids": [str(itsystem_uuid)]},
        }
    )
    assert result == {ituser_uuid}

    result = read_ituser_uuids(
        {
            "itsystem": {"uuids": [str(itsystem_uuid)]},
            "rolebinding": None,
        }
    )
    assert result == set()

    result = read_ituser_uuids(
        {
            "itsystem": {"uuids": [str(itsystem_uuid)]},
            "rolebinding": {"uuids": [str(rolebinding_uuid)]},
        }
    )
    assert result == {ituser_uuid}
