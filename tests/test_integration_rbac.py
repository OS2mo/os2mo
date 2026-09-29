# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID

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
HUM_UNIT = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"


def mock_auth(
    role: str | None = None, user_uuid: UUID | str | None = None
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
        "uuid": str(user_uuid) if user_uuid is not None else None,
    }

    if role is not None:
        token["realm_access"] = {"roles": [role, "service_api"]}

    def fake_auth():
        return Token.parse_obj(token)

    return fake_auth


@pytest.fixture
def users(alice: UUID, bob: UUID) -> dict[str | None, UUID | None]:
    """The token user of a case: Alice owns what the fixtures below give her,
    Bob owns nothing."""
    return {None: None, "alice": alice, "bob": bob}


@pytest.fixture
def classes(
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> dict[str, UUID]:
    """The classes the payloads below refer to."""
    # name: (facet, scope)
    wanted = {
        "institut": ("org_unit_type", None),
        "tjenestetid": ("time_planning", None),
        "niveau": ("org_unit_level", None),
        "linjeorg": ("org_unit_hierarchy", None),
        "telefon": ("org_unit_address_type", "PHONE"),
        "adresse": ("org_unit_address_type", "DAR"),
        "email": ("org_unit_address_type", "EMAIL"),
        "ekstern": ("visibility", None),
    }
    facets = {
        facet: create_facet({"user_key": facet, "validity": {"from": "1970-01-01"}})
        for facet in dict.fromkeys(facet for facet, _ in wanted.values())
    }
    return {
        name: create_class(
            {
                "user_key": name,
                "name": name,
                "facet_uuid": str(facets[facet]),
                "scope": scope,
                "validity": {"from": "1970-01-01"},
            }
        )
        for name, (facet, scope) in wanted.items()
    }


@pytest.fixture
def hum_unit(
    create_org_unit: Callable[..., UUID],
    make_owner: Callable[..., None],
    alice: UUID,
) -> UUID:
    """Humanistisk fakultet, owned by Alice."""
    unit = create_org_unit("hum", validity={"from": "2016-01-01"})
    make_owner(alice, org_unit=unit)
    return unit


@pytest.fixture
def root_unit(create_org_unit: Callable[..., UUID]) -> UUID:
    """A parent nobody owns."""
    return create_org_unit("root")


@pytest.fixture
def create_org_unit_payload(
    root_org: UUID,
    classes: dict[str, UUID],
) -> dict[str, Any]:
    return {
        "name": "Fake Corp",
        "time_planning": {
            "uuid": str(classes["tjenestetid"]),
        },
        "org_unit_type": {"uuid": str(classes["institut"])},
        "org_unit_level": {"uuid": str(classes["niveau"])},
        "org_unit_hierarchy": {"uuid": str(classes["linjeorg"])},
        "details": [
            {
                "type": "address",
                "address_type": {
                    "example": "20304060",
                    "name": "Telefon",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": str(classes["telefon"]),
                },
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": str(root_org),
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
                    "uuid": str(classes["adresse"]),
                },
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": str(root_org),
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
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, "alice", HTTP_403_FORBIDDEN),
        (ADMIN, "alice", HTTP_201_CREATED),
    ],
)
def test_create_org_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    users: dict[str | None, UUID | None],
    root_unit: UUID,
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
    :param userid: the user, see `users`
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, users[userid])

    payload = create_org_unit_payload
    payload["parent"] = {"uuid": str(root_unit)}
    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, "alice", HTTP_403_FORBIDDEN),
        (ADMIN, "alice", HTTP_201_CREATED),
    ],
)
def test_create_top_level_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    users: dict[str | None, UUID | None],
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
    :param userid: the user, see `users`
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, users[userid])

    payload = create_org_unit_payload
    response = service_client.request("POST", "/service/ou/create", json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, "bob", HTTP_403_FORBIDDEN),
        (OWNER, "alice", HTTP_403_FORBIDDEN),
        (ADMIN, "bob", HTTP_200_OK),
    ],
)
def test_rename_org_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    users: dict[str | None, UUID | None],
    hum_unit: UUID,
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
    :param userid: the user, see `users`
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, users[userid])

    # Payload for renaming Humanistisk Fakultet
    payload = {
        "type": "org_unit",
        "data": {
            "name": "New name",
            "uuid": str(hum_unit),
            "clamp": True,
            "validity": {"from": "2021-07-28"},
        },
    }

    response = service_client.request("POST", "/service/details/edit", json=payload)
    assert response.status_code == status_code


@pytest.fixture
def org_unit_no_details_uuid(
    create_org_unit: Callable[..., UUID],
    org_unit_uuid_1: UUID,
) -> UUID:
    """A child of `org_unit_uuid_1`, so Alice owns it through its parent."""
    return create_org_unit("child", org_unit_uuid_1)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, "bob", HTTP_403_FORBIDDEN),
        (OWNER, "alice", HTTP_403_FORBIDDEN),
        (ADMIN, "bob", HTTP_200_OK),
    ],
)
def test_terminate_org_unit(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    users: dict[str | None, UUID | None],
    org_unit_no_details_uuid: UUID,
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
    :param userid: the user, see `users`
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, users[userid])

    # Payload for terminating the newly created org unit
    payload = {"validity": {"to": datetime.today().strftime("%Y-%m-%d")}}

    url_terminate = f"/service/ou/{org_unit_no_details_uuid}/terminate"

    response = service_client.request("POST", url_terminate, json=payload)
    assert response.status_code == status_code


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, userid, status_code",
    [
        (None, None, HTTP_403_FORBIDDEN),
        (OWNER, "bob", HTTP_403_FORBIDDEN),
        (OWNER, "alice", HTTP_403_FORBIDDEN),
        (ADMIN, "bob", HTTP_201_CREATED),
    ],
)
def test_create_detail(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    users: dict[str | None, UUID | None],
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
    :param userid: the user, see `users`
    :param status_code: the expected HTTP status code
    """
    fastapi_test_app.dependency_overrides[fetch_token] = mock_auth(role, users[userid])

    payload = [address_create_payload]
    response = service_client.request("POST", "/service/details/create", json=payload)
    assert response.status_code == status_code


@pytest.fixture
def address_create_payload(
    root_org: UUID, classes: dict[str, UUID], hum_unit: UUID
) -> dict[str, Any]:
    # Payload for creating detail (email address) on org unit
    payload = {
        "type": "address",
        "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": str(root_org),
        },
        "visibility": {
            "uuid": str(classes["ekstern"]),
            "name": "Må vises externt",
            "user_key": "Ekstern",
            "example": None,
            "scope": "INTERNAL",
            "owner": None,
        },
        "address_type": {
            "uuid": str(classes["email"]),
            "name": "Email",
            "user_key": "EmailUnit",
            "example": None,
            "scope": "EMAIL",
            "owner": None,
        },
        "value": "bruce@kung.fu",
        "validity": {"from": "2020-06-22", "to": None},
        "org_unit": {"uuid": str(hum_unit)},
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
    create_org_unit: Callable[..., UUID],
    make_owner: Callable[..., None],
    alice: UUID,
) -> UUID:
    """A unit owned by Alice."""
    unit = create_org_unit("parent")
    make_owner(alice, org_unit=unit)
    return unit
