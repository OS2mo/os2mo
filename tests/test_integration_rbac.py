# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_403_FORBIDDEN

from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import fetch_token
from mora.mapping import ADMIN
from mora.mapping import OWNER

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"

# Org units
ROOT_UNIT = "2874e1dc-85e6-4269-823a-e1125484dfd3"
HUM_UNIT = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"


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
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, userid)

    payload = create_org_unit_payload
    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == status_code


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
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, userid)

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
        (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
        (ADMIN, FEDTMULE, HTTP_200_OK),
    ],
)
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
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, userid)

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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, FEDTMULE, HTTP_403_FORBIDDEN),
        (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
        (ADMIN, FEDTMULE, HTTP_201_CREATED),
    ],
)
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
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, userid)

    payload = [address_create_payload]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


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
        (OWNER, ANDERS_AND, HTTP_403_FORBIDDEN),
        (ADMIN, FEDTMULE, HTTP_200_OK),
    ],
)
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
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, userid)

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


@pytest.fixture
def org_unit_uuid_1(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    create_org_unit_payload: dict[str, Any],
) -> str:
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(ADMIN, FEDTMULE)

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
