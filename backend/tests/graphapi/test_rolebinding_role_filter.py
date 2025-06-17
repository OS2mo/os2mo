# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


@pytest.fixture
def create_ituser(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
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
        return UUID(response.data["ituser_create"]["uuid"])

    return inner


@pytest.fixture
def create_rolebinding(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
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
        return UUID(response.data["rolebinding_create"]["uuid"])

    return inner


@pytest.fixture
def read_rolebinding_uuids(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[UUID]]:
    def inner(filter: dict[str, Any]) -> set[UUID]:
        rolebinding_uuid_query = """
            query ReadRoleBindings($filter: RoleBindingFilter) {
                rolebindings(filter: $filter) {
                    objects {
                        uuid
                    }
                }
            }
        """
        response = graphapi_post(rolebinding_uuid_query, {"filter": filter})
        assert response.errors is None
        assert response.data
        return {UUID(obj["uuid"]) for obj in response.data["rolebindings"]["objects"]}

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_rolebinding_role_filter(
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    read_rolebinding_uuids: Callable[[dict[str, Any]], set[UUID]],
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
    admin_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    reader_class_uuid = create_class(
        {
            "user_key": "reader",
            "name": "Read-only",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

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

    result = read_rolebinding_uuids({})
    assert result == set()

    admin_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_admin",
            "ituser": str(ituser_uuid),
            "role": str(admin_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )
    reader_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_reader",
            "ituser": str(ituser_uuid),
            "role": str(reader_class_uuid),
            "validity": {"from": "2024-01-01"},
        }
    )

    result = read_rolebinding_uuids({})
    assert result == {admin_rolebinding_uuid, reader_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"uuids": [str(admin_class_uuid)]}},
    )
    assert result == {admin_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"uuids": [str(reader_class_uuid)]}},
    )
    assert result == {reader_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"uuids": [str(admin_class_uuid), str(reader_class_uuid)]}},
    )
    assert result == {admin_rolebinding_uuid, reader_rolebinding_uuid}

    result = read_rolebinding_uuids(
        {"role": {"it_system": {"uuids": [str(itsystem_uuid)]}}},
    )
    assert result == {admin_rolebinding_uuid, reader_rolebinding_uuid}
