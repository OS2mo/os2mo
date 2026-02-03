# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from ..conftest import GraphAPIPost


@pytest.fixture
def terminate_rolebinding(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        rolebinding_terminate_mutation = """
            mutation RoleBindingTerminate($input: RoleBindingTerminateInput!) {
                rolebinding_terminate(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(rolebinding_terminate_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["rolebinding_terminate"]["uuid"])

    return inner


@pytest.fixture
def delete_rolebinding(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[UUID], UUID]:
    def inner(uuid: UUID) -> UUID:
        rolebinding_delete_mutation = """
            mutation RoleBindingDelete($uuid: UUID!) {
                rolebinding_delete(uuid: $uuid) {
                    uuid
                }
            }
        """
        response = graphapi_post(rolebinding_delete_mutation, {"uuid": str(uuid)})
        assert response.errors is None
        assert response.data
        return UUID(response.data["rolebinding_delete"]["uuid"])

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_rolebinding_delete(
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    terminate_rolebinding: Callable[[dict[str, Any]], UUID],
    delete_rolebinding: Callable[[UUID], UUID],
    read_rolebinding_uuids: Callable[[dict[str, Any]], set[UUID]],
) -> None:
    """Test that we can filter by rolebindings on itusers."""
    # Create new itsystem
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "1970-01-01"},
        }
    )

    # Create a rolebinding role
    admin_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Create a person
    person_uuid = create_person(
        {
            "given_name": "Xylia",
            "surname": "Shadowthorn",
        }
    )

    # Create an ituser for the person under the itsystem
    ituser_uuid = create_ituser(
        {
            "user_key": "xylia",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Read all role-bindings across all time
    result = read_rolebinding_uuids({"from_date": None, "to_date": None})
    assert result == set()

    # Create a rolebinding for our ituser with the the role
    admin_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_admin",
            "ituser": str(ituser_uuid),
            "role": str(admin_class_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Read our newly created role-binding
    result = read_rolebinding_uuids({"from_date": None, "to_date": None})
    assert result == {admin_rolebinding_uuid}

    # Terminate our rolebinding
    terminate_rolebinding({"uuid": str(admin_rolebinding_uuid), "to": "1980-01-01"})

    # Read our now terminated role-binding
    result = read_rolebinding_uuids({"from_date": None, "to_date": None})
    assert result == {admin_rolebinding_uuid}

    # Delete our rolebinding
    delete_rolebinding(admin_rolebinding_uuid)

    # The role-binding should now be entirely gone as if it never existed
    result = read_rolebinding_uuids({"from_date": None, "to_date": None})
    assert result == set()


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_rolebinding_registration_read(
    graphapi_post: GraphAPIPost,
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_rolebinding: Callable[[dict[str, Any]], UUID],
    terminate_rolebinding: Callable[[dict[str, Any]], UUID],
    delete_rolebinding: Callable[[UUID], UUID],
    read_rolebinding_uuids: Callable[[dict[str, Any]], set[UUID]],
) -> None:
    """Test that we can filter by rolebindings on itusers."""
    # Create new itsystem
    itsystem_uuid = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "1970-01-01"},
        }
    )

    # Create a rolebinding role
    admin_class_uuid = create_class(
        {
            "user_key": "admin",
            "name": "Administrator",
            "facet_uuid": str(role_facet),
            "it_system_uuid": str(itsystem_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Create a person
    person_uuid = create_person(
        {
            "given_name": "Xylia",
            "surname": "Shadowthorn",
        }
    )

    # Create an ituser for the person under the itsystem
    ituser_uuid = create_ituser(
        {
            "user_key": "xylia",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Read all role-bindings across all time
    result = read_rolebinding_uuids({"from_date": None, "to_date": None})
    assert result == set()

    # Create a rolebinding for our ituser with the the role
    admin_rolebinding_uuid = create_rolebinding(
        {
            "user_key": "xylia_admin",
            "ituser": str(ituser_uuid),
            "role": str(admin_class_uuid),
            "validity": {"from": "1970-01-01"},
        }
    )

    # Read our newly created role-binding
    result = read_rolebinding_uuids({"from_date": None, "to_date": None})
    assert result == {admin_rolebinding_uuid}

    query = """
        query ReadRolebindingRegistration($uuid: [UUID!]) {
            registrations(filter: {uuids: $uuid}) {
                objects {
                    ... on RoleBindingRegistration {
                        uuid
                    }
                }
            }
        }
    """

    response = graphapi_post(query, {"uuid": str(admin_rolebinding_uuid)})
    assert response.errors is None
    assert response.data
