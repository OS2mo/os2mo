# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER
from mora.mapping import PERSON
from mora.mapping import UUID
from more_itertools import one
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_400_BAD_REQUEST
from starlette.status import HTTP_403_FORBIDDEN

from tests.test_integration_rbac import mock_auth
from tests.util import jsonfile_to_dict
from tests.util import override_config

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"
LIS_JENSEN = "7626ad64-327d-481f-8b32-36c78eb12f8c"
ERIK_SMIDT_HANSEN = "236e0a78-11a0-4ed9-8545-6286bb8611c7"


def parametrize_roles_code(status_code: int) -> Callable:
    def wrapper(func: Callable) -> Callable:
        return pytest.mark.parametrize(
            "role, userid, status_code",
            # Test of write access for the following cases:
            [
                # 1) Normal user (no roles set)
                (None, None, HTTP_403_FORBIDDEN),
                # 2) User with the owner role, but not owner of the relevant entity
                (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
                # 3) User with the owner role and owner of the relative entity
                (OWNER, ANDERS_AND, status_code),
                # 4) User with the admin role
                (ADMIN, FEDTMULE, status_code),
            ],
        )(func)

    return wrapper


parametrize_roles = parametrize_roles_code(HTTP_200_OK)
parametrize_roles_create = parametrize_roles_code(HTTP_201_CREATED)


@pytest.fixture
def create_employee_owner_payload() -> dict[str, Any]:
    payload = one(jsonfile_to_dict("tests/fixtures/rbac/create_employee_owner.json"))
    payload[OWNER][UUID] = ANDERS_AND
    payload[PERSON][UUID] = LIS_JENSEN
    return payload


@pytest.fixture
async def create_lis_owner(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employee_owner_payload: dict[str, Any],
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

    payload = create_employee_owner_payload
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201


@pytest.fixture
async def create_fedtmule_owner(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employee_owner_payload: dict[str, Any],
) -> None:
    # Let Anders And be the owner of Erik Smidt Hansen
    fastapi_test_app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

    payload = create_employee_owner_payload
    payload[PERSON][UUID] = FEDTMULE

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201


@pytest.fixture
async def create_erik_owner(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employee_owner_payload: dict[str, Any],
) -> None:
    # Let Anders And be the owner of Erik Smidt Hansen
    fastapi_test_app.dependency_overrides[auth] = mock_auth(ADMIN, ANDERS_AND)

    payload = create_employee_owner_payload
    payload[PERSON][UUID] = ERIK_SMIDT_HANSEN

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201


@pytest.fixture
def create_it_system_payload() -> dict[str, Any]:
    return {
        "type": "it",
        "user_key": "AD",
        "person": {"uuid": LIS_JENSEN},
        "itsystem": {"uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"},
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "validity": {"from": "2021-08-11", "to": None},
    }


@pytest.fixture
def create_employee_payload() -> dict[str, Any]:
    payload = one(jsonfile_to_dict("tests/fixtures/rbac/create_employee_detail.json"))
    payload["person"]["uuid"] = LIS_JENSEN
    return payload


@pytest.fixture
def create_employment_payload(
    create_employee_payload: dict[str, Any],
) -> dict[str, Any]:
    payload = create_employee_payload
    payload["type"] = "engagement"
    payload["job_function"] = {
        "uuid": "f42dd694-f1fd-42a6-8a97-38777b73adc4",
        "name": "Bogopsætter",
        "user_key": "Bogopsætter",
        "example": None,
        "scope": None,
        "owner": None,
    }
    payload["engagement_type"] = {
        "uuid": "06f95678-166a-455a-a2ab-121a8d92ea23",
        "name": "Ansat",
        "user_key": "ansat",
        "example": None,
        "scope": None,
        "owner": None,
    }
    return payload


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    # Test of write access for the following cases:
    [
        # 1) Normal user (no roles set)
        (None, None, HTTP_403_FORBIDDEN),
        # 2) User with owner role
        (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
        # 3) User with the admin role
        (ADMIN, ANDERS_AND, HTTP_201_CREATED),
    ],
)
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_employee(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)
    response = service_client.request(
        "POST",
        "/service/e/create",
        json={
            "name": "Mickey Mouse",
            "nickname_givenname": "",
            "cpr_no": "1111111111",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "details": [],
        },
    )
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@parametrize_roles_create
@override_config(Settings(keycloak_rbac_enabled=True))
def test_creating_detail_address(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    # Payload for creating detail (phone number) on employee
    payload = one(
        jsonfile_to_dict("tests/fixtures/rbac/create_employee_detail_phone.json")
    )
    payload[PERSON][UUID] = LIS_JENSEN

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_201_when_creating_it_system_detail_as_owner_of_employee(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_it_system_payload: dict[str, Any],
) -> None:
    # Use user "Anders And" (who owns the employee)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = [create_it_system_payload]

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_201_when_creating_multiple_it_system_details_as_owner_of_employee(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_it_system_payload: dict[str, Any],
) -> None:
    # Use user "Anders And" (who owns the employee)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = [create_it_system_payload, create_it_system_payload]

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == HTTP_201_CREATED


# When creating employee details in the frontend some details actually
# resides under an org unit, e.g. employment, role, association, ...
# A selection of these details are tested here (with respect to creating details)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@parametrize_roles_create
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_employment(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employment_payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = create_employment_payload

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_multiple_employments_owns_one_unit_but_not_the_other(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
) -> None:
    # Use user "Anders And" (who owns one unit but not the other)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = jsonfile_to_dict("tests/fixtures/rbac/create_multiple_employments.json")
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_multiple_employments_owns_all_units(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employment_payload: dict[str, Any],
) -> None:
    # Use user "Anders And" (who owns all units)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = [create_employment_payload, create_employment_payload]

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_multiple_associations_owns_one_unit_but_not_the_other(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
) -> None:
    # Use user "Anders And" (who owns one unit but not the other)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    create_multiple_associations = jsonfile_to_dict(
        "tests/fixtures/rbac/create_multiple_associations.json"
    )
    payload = create_multiple_associations

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_multiple_associations_owns_all_units(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
) -> None:
    # Use user "Anders And" (who owns all units)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    create_multiple_associations = jsonfile_to_dict(
        "tests/fixtures/rbac/create_multiple_associations.json"
    )
    create_multiple_associations[1] = create_multiple_associations[0]
    payload = create_multiple_associations

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == HTTP_201_CREATED


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@parametrize_roles_create
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_association(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employee_payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = create_employee_payload
    payload["type"] = "association"
    payload["association_type"] = {
        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
        "name": "Medlem",
        "user_key": "medl",
        "example": None,
        "scope": None,
        "owner": None,
    }

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@parametrize_roles_create
@override_config(Settings(keycloak_rbac_enabled=True))
def test_create_manager(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_employee_payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = create_employee_payload
    payload["type"] = "manager"
    payload["manager_type"] = {
        "uuid": "0d72900a-22a4-4390-a01e-fd65d0e0999d",
        "name": "Direktør",
        "user_key": "Direktør",
        "example": None,
        "scope": None,
        "owner": None,
    }
    payload["manager_level"] = {
        "uuid": "3c791935-2cfa-46b5-a12e-66f7f54e70fe",
        "name": "Niveau 1",
        "user_key": "Niveau1",
        "example": None,
        "scope": None,
        "owner": None,
    }
    payload["responsibility"] = [
        {
            "uuid": "93ea44f9-127c-4465-a34c-77d149e3e928",
            "name": "Beredskabsledelse",
            "user_key": "Beredskabsledelse",
            "example": None,
            "scope": None,
            "owner": None,
        }
    ]

    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@override_config(Settings(keycloak_rbac_enabled=True))
def test_object_types_in_list_must_be_identical(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
) -> None:
    # Use user "Anders And" (who owns all units)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    create_multiple_associations = jsonfile_to_dict(
        "tests/fixtures/rbac/create_multiple_associations.json"
    )
    create_multiple_associations[1] = deepcopy(create_multiple_associations[0])
    create_multiple_associations[1]["type"] = "address"

    response = service_client.request(
        "POST", "/service/details/create", json=create_multiple_associations
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(
    "fixture",
    [
        "edit_address",
        "edit_association",
        "edit_employment",
        "edit_manager",
        "move_employment",
        "move_multiple_employments",
    ],
)
@parametrize_roles
@override_config(Settings(keycloak_rbac_enabled=True))
def test_edit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    fixture: str,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = jsonfile_to_dict(f"tests/fixtures/rbac/{fixture}.json")
    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(
    "payload",
    [
        # Address
        {
            "type": "address",
            "uuid": "64ea02e2-8469-4c54-a523-3d46729e86a7",
            "validity": {"to": "2021-08-20"},
        },
        # Engagement
        {
            "type": "engagement",
            "uuid": "301a906b-ef51-4d5c-9c77-386fb8410459",
            "validity": {"to": "2021-08-13"},
        },
    ],
)
@parametrize_roles
@override_config(Settings(keycloak_rbac_enabled=True))
def test_terminate_details(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)
    response = service_client.request(
        "POST", "/service/details/terminate", json=payload
    )
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@parametrize_roles
@override_config(Settings(keycloak_rbac_enabled=True))
def test_terminate_employee(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)
    response = service_client.request(
        "POST",
        f"/service/e/{LIS_JENSEN}/terminate",
        json={"validity": {"to": "2021-08-17"}},
    )
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_erik_owner")
@parametrize_roles_create
@override_config(Settings(keycloak_rbac_enabled=True))
def test_employee_leave(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)
    payload = jsonfile_to_dict("tests/fixtures/rbac/leave.json")
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code
