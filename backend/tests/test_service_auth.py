# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.routing import APIWebSocketRoute
from fastapi.testclient import TestClient
from more_itertools import one
from os2mo_fastapi_utils.auth.exceptions import AuthenticationError
from os2mo_fastapi_utils.auth.models import RealmAccess
from os2mo_fastapi_utils.auth.test_helper import (
    ensure_endpoints_depend_on_oidc_auth_function,
)
from os2mo_fastapi_utils.auth.test_helper import (
    ensure_no_auth_endpoints_do_not_depend_on_auth_function,
)
from pydantic import MissingError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

import mora.auth.keycloak.oidc
from mora.auth.keycloak.models import KeycloakToken
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from mora.graphapi.main import graphql_versions
from tests import util
from tests.conftest import get_latest_graphql_url


@pytest.fixture(scope="session")
def no_auth_endpoints():
    """Fixture yielding endpoint URL paths that should not have authentication."""
    no_auth_endpoints = {
        "/health/",
        "/health/live",
        "/health/ready",
        "/health/{identifier}",
        "/version/",
        "/service/keycloak.json",
        "/service/token",
        "/service/exports/{file_name}",
        "/service/{rest_of_path:path}",
        "/testing/testcafe-db-setup",
        "/testing/testcafe-db-teardown",
        "/metrics",
        "/saml/sso/",
        "/graphql",
        "/graphql/v{version_number}",
    }
    graphql_endpoints = {f"/graphql/v{version.version}" for version in graphql_versions}

    yield no_auth_endpoints | graphql_endpoints


@pytest.fixture(scope="session")
def all_routes(fastapi_test_app: FastAPI) -> list[APIRoute]:
    """Fixture yields all routes defined in the FASTAPI app, excluding endpoints that
    which are NOT to be evaluated."""
    # List of endpoints to not evaluate
    skip_endpoints = {
        # This URL has both a protected and unprotected endpoint
        "/service/exports/{file_name}",
    }
    routes = fastapi_test_app.routes
    routes = filter(lambda route: not isinstance(route, APIWebSocketRoute), routes)
    routes = filter(lambda route: route.path not in skip_endpoints, routes)
    return list(routes)


def test_ensure_endpoints_depend_on_oidc_auth_function(all_routes, no_auth_endpoints):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below)
    """
    # No fancy logic (for security reasons) to set the excluded endpoints -
    # all excluded endpoints must be explicitly specified in the list

    ensure_endpoints_depend_on_oidc_auth_function(
        all_routes, no_auth_endpoints, mora.auth.keycloak.oidc.auth
    )


def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(
    all_routes, no_auth_endpoints
):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below)
    """
    # No fancy logic (for security reasons) to set the excluded endpoints -
    # all excluded endpoints must be explicitly specified in the list

    ensure_no_auth_endpoints_do_not_depend_on_auth_function(
        all_routes, no_auth_endpoints, mora.auth.keycloak.oidc.auth
    )


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "url",
    [
        "/service/e/00000000-0000-0000-0000-000000000000/details/address",
        "/service/e/cpr_lookup/?q=1234",
        "/service/e/00000000-0000-0000-0000-000000000000/details/",
        "/service/o/00000000-0000-0000-0000-000000000000/e/",
        "/service/exports/not-important",
        "/service/c/ancestor-tree",
        "/service/o/00000000-0000-0000-0000-000000000000/it/",
        "/service/o/",
        "/service/ou/00000000-0000-0000-0000-000000000000/children",
        "/service/ou/00000000-0000-0000-0000-000000000000/configuration",
    ],
)
async def test_auth_service(raw_client: TestClient, url: str) -> None:
    response = raw_client.get(url)
    assert response.status_code == 401
    # assert response.text == '"Not authenticated"'


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "url",
    [
        "/service/details/create",
        "/service/ou/00000000-0000-0000-0000-000000000000/map",
        "/service/validate/org-unit/",
    ],
)
async def test_auth_service_with_payload(raw_client: TestClient, url: str) -> None:
    response = raw_client.post(url, json=[{"not": "important"}])
    assert response.status_code == 401
    assert response.text == '"Not authenticated"'


async def test_no_auth_graphql(raw_client: TestClient) -> None:
    response = raw_client.post(
        get_latest_graphql_url(), json={"query": "{ org { uuid } }"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": None,
        "errors": [
            {
                "locations": [{"column": 3, "line": 1}],
                "message": "Not authenticated",
                "path": ["org"],
            }
        ],
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures_minimal")
def test_auth_service_org(raw_client: TestClient, auth_headers: dict[str, str]) -> None:
    response = raw_client.get("/service/o/", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures_minimal")
async def test_auth_graphql(
    raw_client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = raw_client.post(
        get_latest_graphql_url(),
        headers=auth_headers,
        json={"query": "{ org { uuid } }"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"}}
    }


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_required_if_client_is_mo():
    with pytest.raises(ValidationError) as err:
        KeycloakToken(azp="mo-frontend", realm_access=RealmAccess(roles={"owner"}))
    # Testing for one error only.
    error = one(err.value.errors())

    assert error["msg"] == "The uuid user attribute is required for owners."
    assert error["type"] == "value_error"
    assert len(err.value.errors()) == 1


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_parsed_correctly_uuid():
    token = KeycloakToken(
        azp="mo-frontend", uuid="30c89ad2-e0bb-42ae-82a8-1ae36943cb9e"
    )
    assert token.uuid == UUID("30c89ad2-e0bb-42ae-82a8-1ae36943cb9e")


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_parsed_correctly_base64():
    token = KeycloakToken(azp="mo-frontend", uuid="0prIMLvgrkKCqBrjaUPLng==")

    assert token.uuid == UUID("30c89ad2-e0bb-42ae-82a8-1ae36943cb9e")


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_parse_fails_on_garbage():
    with pytest.raises(ValidationError) as err:
        KeycloakToken(
            azp="mo-frontend",
            realm_access=RealmAccess(roles={"owner"}),
            uuid="garbageasdasd",
        )
    errors = err.value.errors()[0]

    assert errors["msg"] == "value is not a valid uuid"
    assert errors["type"] == "type_error.uuid"
    assert len(err.value.errors()) == 2


@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures_minimal")
def test_401_when_uuid_missing_in_token(
    raw_client: TestClient, auth_headers: dict[str, str]
) -> None:
    validation_err = ValidationError(
        errors=[ErrorWrapper(MissingError(), loc="uuid")], model=Token
    )

    def fake_auth():
        raise AuthenticationError(exc=validation_err)

    app = raw_client.app
    app.dependency_overrides[auth] = fake_auth

    # Make call to random endpoint
    response = raw_client.get("/service/o/", headers=auth_headers)
    assert response.status_code == 401
    assert response.json() == {"status": "Unauthorized", "msg": str(validation_err)}
