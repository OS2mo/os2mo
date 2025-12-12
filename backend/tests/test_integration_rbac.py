# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.rbac import _get_employee_uuid_via_it_system
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_403_FORBIDDEN

from tests import util

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"

# Org units
ROOT_UNIT = "2874e1dc-85e6-4269-823a-e1125484dfd3"
HUM_UNIT = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
FILOSOFISK_INSTITUT = "85715fc7-925d-401b-822d-467eb4b163b6"

# IT systems
ACTIVE_DIRECTORY = UUID("59c135c9-2b15-41cc-97c8-b5dff7180beb")

# IT users
ANDERS_AND_AD_USER_KEY = "18d2271a-45c4-406c-a482-04ab12f80881"
ANDERS_AND_AD_EXTERNAL_ID = "e5595d6a-590c-4cae-9164-9fcf8e1178a2"


def mock_auth(
    role: str | None = None, user_uuid: str | None = None
) -> Callable[[], Token]:
    """
    Create auth for a user with the given role (admin or owner) and the given
    user UUID
    """

    token = {
        "acr": "1",
        "allowed-origins": ["http://localhost:5001"],
        "azp": "vue",
        "email": "bruce@kung.fu",
        "email_verified": False,
        "exp": 1621779689,
        "family_name": "Lee",
        "given_name": "Bruce",
        "iat": 1621779389,
        "iss": "http://localhost:8081/auth/realms/mo",
        "jti": "25dbb58d-b3cb-4880-8b51-8b92ada4528a",
        "name": "Bruce Lee",
        "preferred_username": "bruce",
        "scope": "email profile",
        "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
        "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
        "typ": "Bearer",
        "uuid": user_uuid,
    }

    if role is not None:
        token["realm_access"] = {"roles": [role, "service_api"]}

    def fake_auth():
        return Token.parse_obj(token)

    return fake_auth


@pytest.fixture
def create_org_unit_payload() -> dict[str, Any]:
    return {
        "name": "Fake Corp",
        "time_planning": {
            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
        },
        "parent": {"uuid": ROOT_UNIT},
        "org_unit_type": {"uuid": "ca76a441-6226-404f-88a9-31e02e420e52"},
        "org_unit_level": {"uuid": "0f015b67-f250-43bb-9160-043ec19fad48"},
        "org_unit_hierarchy": {"uuid": "12345678-abcd-abcd-1234-12345678abcd"},
        "details": [
            {
                "type": "address",
                "address_type": {
                    "example": "20304060",
                    "name": "Telefon",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                },
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "validity": {
                    "from": "2016-02-04",
                    "to": None,
                },
                "value": "11223344",
            },
            {
                "type": "address",
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                },
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                },
                "validity": {
                    "from": "2016-02-04",
                    "to": None,
                },
                "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
            },
        ],
        "validity": {
            "from": "2016-02-04",
            "to": None,
        },
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
        (ADMIN, ANDERS_AND, HTTP_201_CREATED),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_create_org_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the admin role

    :param role: the role of the user
    :param userid: the UUID of the user
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = create_org_unit_payload
    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_201_when_creating_unit_as_owner_of_parent_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = create_org_unit_payload
    payload["parent"]["uuid"] = HUM_UNIT

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 201


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
        (ADMIN, ANDERS_AND, HTTP_201_CREATED),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_create_top_level_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role
    3) User with the admin role

    :param role: the role of the user
    :param userid: the UUID of the user
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = create_org_unit_payload
    payload.pop("parent")

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_200_OK),
        (ADMIN, FEDTMULE, HTTP_200_OK),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_rename_org_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role

    :param role: the role of the user
    :param userid: the UUID of the user
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    # Payload for renaming Humanistisk Fakultet
    payload = {
        "type": "org_unit",
        "data": {
            "name": "New name",
            "uuid": HUM_UNIT,
            "clamp": True,
            "validity": {"from": "2021-07-28"},
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == status_code


@pytest.fixture
def org_unit_no_details_uuid(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
    org_unit_uuid_1: str,
) -> str:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

    create_org_unit_payload["details"] = []
    create_org_unit_payload["parent"]["uuid"] = org_unit_uuid_1

    payload = create_org_unit_payload

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_200_OK),
        (ADMIN, FEDTMULE, HTTP_200_OK),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_terminate_org_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    org_unit_no_details_uuid: str,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role

    :param role: the role of the user
    :param userid: the UUID of the user
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    # Payload for terminating the newly created org unit
    payload = {"validity": {"to": datetime.today().strftime("%Y-%m-%d")}}

    url_terminate = f"/service/ou/{org_unit_no_details_uuid}/terminate"

    response = service_client.request("POST", url_terminate, json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_201_CREATED),
        (ADMIN, FEDTMULE, HTTP_201_CREATED),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_create_detail(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    address_create_payload: dict[str, Any],
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role

    :param role: the role of the user
    :param userid: the UUID of the user
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = [address_create_payload]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_201_when_creating_multiple_details_as_owner_of_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    address_create_payload: dict[str, Any],
) -> None:
    # Use user "Anders And" (who owns the unit)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = [address_create_payload, address_create_payload]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 201


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_400_when_creating_multiple_details_with_different_types(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    address_create_payload: dict[str, Any],
) -> None:
    # Use user "Anders And" (who owns the unit)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    payload = [
        address_create_payload,
        {
            **address_create_payload,
            "type": "org_unit",
        },
    ]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == 400


@pytest.fixture
def address_create_payload() -> dict[str, Any]:
    # Payload for creating detail (email address) on org unit
    payload = {
        "type": "address",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "visibility": {
            "uuid": "f63ad763-0e53-4972-a6a9-63b42a0f8cb7",
            "name": "Må vises externt",
            "user_key": "Ekstern",
            "example": None,
            "scope": "INTERNAL",
            "owner": None,
        },
        "address_type": {
            "uuid": "73360db1-bad3-4167-ac73-8d827c0c8751",
            "name": "Email",
            "user_key": "EmailUnit",
            "example": None,
            "scope": "EMAIL",
            "owner": None,
        },
        "value": "bruce@kung.fu",
        "validity": {"from": "2020-06-22", "to": None},
        "org_unit": {"uuid": HUM_UNIT},
    }
    return payload


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_200_OK),
        (ADMIN, FEDTMULE, HTTP_200_OK),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_edit_detail(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role

    :param role: the role of the user
    :param userid: the UUID of the user
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    # Payload for editing detail (phone number) on org unit (hum)
    payload = {
        "type": "address",
        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
        "data": {
            "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
            "user_key": "8715 0000",
            "validity": {"from": "2021-07-29", "to": None},
            "address_type": {
                "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                "name": "Telefon",
                "user_key": "OrgEnhedTelefon",
                "example": "20304060",
                "scope": "PHONE",
                "owner": None,
            },
            "href": "tel:+4587150000",
            "name": "+4587150000",
            "value": "+4587150001",
            "value2": None,
            "visibility": {
                "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                "name": "Telefon",
                "user_key": "OrgEnhedTelefon",
                "example": "20304060",
                "scope": "PHONE",
                "owner": None,
            },
            "org_unit": {
                "name": "Humanistisk fakultet",
                "user_key": "hum",
                "uuid": HUM_UNIT,
                "validity": {"from": "2016-01-01", "to": None},
            },
            "type": "address",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
        },
        "org_unit": {"uuid": HUM_UNIT},
    }

    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (OWNER, ANDERS_AND, HTTP_200_OK),
        (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_rename_subunit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    org_unit_uuid_2: str,
    role: str,
    userid: str,
    status_code: int,
) -> None:
    """
    Test that an org unit can be modified by a user who owns the parent
    unit but not the unit subject to modification itself.
    """
    fastapi_test_app.dependency_overrides[auth] = mock_auth(role, userid)

    payload = {
        "type": "org_unit",
        "data": {
            "name": "New name",
            "uuid": org_unit_uuid_2,
            "clamp": True,
            "validity": {"from": "2021-07-28"},
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == status_code


@pytest.fixture
def org_unit_uuid_1(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
) -> str:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

    payload = create_org_unit_payload

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 201
    org_uuid = response.json()

    create_owner_payload = {
        "type": "owner",
        "owner": {
            "givenname": "Anders",
            "surname": "And",
            "name": "Anders And",
            "nickname_givenname": "Donald",
            "nickname_surname": "Duck",
            "nickname": "Donald Duck",
            "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "seniority": None,
            "cpr_no": "0906340000",
            "org": {
                "name": "Aarhus Universitet",
                "user_key": "AU",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            },
            "user_key": "andersand",
        },
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        },
        "validity": {"from": "2021-08-03", "to": None},
        "org_unit": {"uuid": org_uuid},
    }

    response = service_client.request(
        "POST", "/service/details/create", json=create_owner_payload
    )
    assert response.status_code == 201

    return org_uuid


@pytest.fixture
def org_unit_uuid_2(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
    org_unit_uuid_1: str,
) -> str:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(ADMIN, FEDTMULE)

    create_org_unit_payload["parent"]["uuid"] = org_unit_uuid_1
    payload = create_org_unit_payload

    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "owner,org_uuid,one_is_parent,status_code",
    [
        # test_owner_of_unit_moves_unit_to_owned_unit
        (ANDERS_AND, HUM_UNIT, True, 200),
        # test_owner_of_unit_moves_unit_to_subunit_of_owned_unit
        (ANDERS_AND, HUM_UNIT, False, 200),
        # test_non_owner_of_unit_moves_unit_to_non_owned_unit
        (FEDTMULE, HUM_UNIT, True, 403),
        # test_non_owner_of_unit_moves_unit_to_subunit_of_non_owned_unit
        (FEDTMULE, HUM_UNIT, False, 403),
        # test_owner_moves_owned_subunit_to_owned_subunit
        (ANDERS_AND, FILOSOFISK_INSTITUT, False, 200),
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_owner_of_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    org_unit_uuid_1: str,
    org_unit_uuid_2: str,
    owner: str,
    org_uuid: str,
    one_is_parent: bool,
    status_code: int,
) -> None:
    # Use user "Anders And" (who owns the parent unit)
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, owner)

    parent_uuid = org_unit_uuid_1 if one_is_parent else org_unit_uuid_2

    payload = {
        "type": "org_unit",
        "data": {
            "parent": {"uuid": parent_uuid},
            "uuid": org_uuid,
            "clamp": True,
            "validity": {"from": "2021-07-30"},
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "payload",
    [
        {
            "type": "address",
            "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
            "validity": {"to": "2021-07-16"},
        },
        {
            "type": "association",
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "validity": {"to": "2021-07-16"},
        },
        {
            "type": "manager",
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "validity": {"to": "2021-07-16"},
        },
        {
            "type": "org_unit",
            "uuid": HUM_UNIT,
            "validity": {"to": "2021-07-16"},
        },
    ],
)
@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_terminate_x_as_owner_of_unit(
    fastapi_test_app: FastAPI, service_client: TestClient, payload: dict[str, Any]
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, ANDERS_AND)

    response = service_client.request(
        "POST", "/service/details/terminate", json=payload
    )
    assert response.status_code == 200
    assert response.json() == payload["uuid"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "token_uuid,expected",
    [
        (ANDERS_AND_AD_USER_KEY, 403),
        (ANDERS_AND_AD_EXTERNAL_ID, 200),
        (ANDERS_AND, 403),
    ],
)
@util.override_config(
    Settings(
        keycloak_rbac_enabled=True,
        keycloak_rbac_authoritative_it_system_for_owners=ACTIVE_DIRECTORY,
    )
)
def test_ownership_through_it_system(
    fastapi_test_app: FastAPI, service_client: TestClient, token_uuid, expected
) -> None:
    fastapi_test_app.dependency_overrides[auth] = mock_auth(OWNER, token_uuid)

    payload = {
        "type": "address",
        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
        "validity": {"to": "2021-07-16"},
    }

    response = service_client.request(
        "POST", "/service/details/terminate", json=payload
    )

    assert response.status_code == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_it_user_to_employee_uuid():
    result = await _get_employee_uuid_via_it_system(
        ACTIVE_DIRECTORY, ANDERS_AND_AD_EXTERNAL_ID
    )
    assert ANDERS_AND == str(result)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_it_user_to_employee_uuid_missing_it_user():
    with pytest.raises(AuthorizationError):
        await _get_employee_uuid_via_it_system(ACTIVE_DIRECTORY, uuid4())
