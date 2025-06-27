# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from tests.conftest import GraphAPIPost
from more_itertools import one
import pytest


@pytest.fixture
def create_address(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        address_create_mutation = """
            mutation AddressCreate($input: AddressCreateInput!) {
                address_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(address_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["address_create"]["uuid"])

    return inner


@pytest.fixture
def update_class(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        class_update_mutation = """
            mutation UpdateClass($input: ClassUpdateInput!) {
                class_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(class_update_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        class_uuid = UUID(response.data["class_update"]["uuid"])
        return class_uuid

    return inner


@pytest.fixture
def read_class_name(
    graphapi_post: GraphAPIPost
) -> Callable[[UUID], list[dict[str, Any]]]:
    def inner(input: UUID) -> list[dict[str, Any]]:
        address_query = """
            query ReadClassName($uuid: UUID!) {
              classes(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    name
                    validity {
                        from
                        to
                    }
                  }
                }
              }
            }
        """
        response = graphapi_post(address_query, {"uuid": str(input)})
        assert response.errors is None
        assert response.data
        obj = one(response.data["classes"]["objects"])
        return obj["validities"]

    return inner


@pytest.fixture
def read_deprecated_address_type_uuid(
    graphapi_post: GraphAPIPost
) -> Callable[[UUID], UUID]:
    def inner(input: UUID) -> UUID:
        address_query = """
            query ReadAddressUUID($uuid: UUID!) {
              addresses(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    address_type_uuid
                  }
                }
              }
            }
        """
        response = graphapi_post(address_query, {"uuid": str(input)})
        assert response.errors is None
        assert response.data
        obj = one(response.data["addresses"]["objects"])
        validity = one(obj["validities"])
        return UUID(validity["address_type_uuid"])

    return inner


@pytest.fixture
def read_address_type_uuid(
    graphapi_post: GraphAPIPost
) -> Callable[[UUID], UUID]:
    def inner(input: UUID) -> UUID:
        address_query = """
            query ReadAddressUUID($uuid: UUID!) {
              addresses(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    address_type {
                      uuid
                    }
                  }
                }
              }
            }
        """
        response = graphapi_post(address_query, {"uuid": str(input)})
        assert response.errors is None
        assert response.data
        obj = one(response.data["addresses"]["objects"])
        validity = one(obj["validities"])
        return UUID(validity["address_type"]["uuid"])

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_address_response(
    employee_address_type_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
    update_class: Callable[[dict[str, Any]], UUID],
    read_class_name: Callable[[UUID], list[dict[str, Any]]],
    read_deprecated_address_type_uuid: Callable[[UUID], UUID],
    read_address_type_uuid: Callable[[UUID], UUID],
) -> None:
    # Create an address-type and verify it
    employee_phone_class_uuid = create_class(
        {
            "user_key": "PhoneEmployee",
            "name": "Telefon",
            "scope": "PHONE",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "3024-01-01"},
        }
    )
    assert read_class_name(employee_phone_class_uuid) == [{
        "name": "Telefon",
        "validity": {
            "from": "3024-01-01T00:00:00+01:00",
            "to": None
        }
    }]

    
    person_uuid = create_person(
        {
            "given_name": "Seraphina",
            "surname": "Nightshade",
        }
    )

    address_uuid = create_address(
        {
            "value": "12345678",
            "address_type": str(employee_phone_class_uuid),
            "person": str(person_uuid),
            "validity": {"from": "3024-01-01"},
        }
    )

    address_type_uuid = read_deprecated_address_type_uuid(address_uuid)
    assert address_type_uuid == employee_phone_class_uuid

    address_type_uuid = read_address_type_uuid(address_uuid)
    assert address_type_uuid == employee_phone_class_uuid


    # Modify address type class and verify it
    update_class(
        {
            "uuid": str(employee_phone_class_uuid),
            "user_key": "PhoneEmployee",
            "name": "Mobil",
            "scope": "PHONE",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "3026-01-01"},

        }
    )
    assert read_class_name(employee_phone_class_uuid) == [
        # The original validity, now terminated
        {
            "name": "Telefon",
            "validity": {
                "from": "3024-01-01T00:00:00+01:00",
                # This should probably be at 23:59:59, not at 00:00:00
                "to": "3025-12-31T00:00:00+01:00"
            }
        },
        # The new validity
        {
            "name": "Mobil",
            "validity": {
                "from": "3026-01-01T00:00:00+01:00",
                "to": None
            }
        },
    ]

    address_type_uuid = read_deprecated_address_type_uuid(address_uuid)
    assert address_type_uuid == employee_phone_class_uuid

    address_type_uuid = read_address_type_uuid(address_uuid)
    assert address_type_uuid == employee_phone_class_uuid
