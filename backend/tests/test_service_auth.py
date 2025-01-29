# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import mora.auth.keycloak.oidc
import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.routing import APIWebSocketRoute
from fastapi.testclient import TestClient
from mora.auth.exceptions import AuthenticationError
from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.config import Settings
from pydantic import MissingError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

from tests import util

from .conftest import fake_auth
from .conftest import serviceapiless_auth


def lookup_auth_dependency(route, auth_coro):
    # Check if auth dependency exists
    return any(d.dependency == auth_coro for d in route.dependencies)


def ensure_endpoints_depend_on_oidc_auth_function(
    all_routes, no_auth_endpoints, auth_coro
):
    """
    Loop through all FastAPI routes (except the ones from the above
    exclude list) and make sure they depend (via fastapi.Depends) on the
    auth coroutine.

    A little risky since we should avoid "logic" in the test code!
    (so direct auth "requests" tests should also be added)

    :param all_routes: all routes defined in the FastAPI app
    :param no_auth_endpoints: list of all endpoint URL path that should not
    have authentication
    :param auth_coro: the authentication coroutine
    """

    # Skip the starlette.routing.Route's (defined by the framework)
    routes = filter(lambda _route: isinstance(_route, APIRoute), all_routes)
    # Only check endpoints not in the NO_AUTH_ENDPOINTS list
    routes = filter(lambda _route: _route.path not in no_auth_endpoints, routes)
    routes = list(routes)

    # Make sure that routes are defined
    assert routes

    for route in routes:
        has_auth = lookup_auth_dependency(route, auth_coro)
        assert has_auth, f"Route not protected: {route.path}"


def ensure_no_auth_endpoints_do_not_depend_on_auth_function(
    all_routes, no_auth_endpoints, auth_coro
):
    """
    Loop through the FastAPI routes that do not require authentication
    (except the ones from the above exclude list) and make sure they do not
    depend (via fastapi.Depends) on the auth coroutine.

    :param all_routes: all routes defined in the FastAPI app
    :param no_auth_endpoints: list of all endpoint URL path that should not
    have authentication
    :param auth_coro: the authentication coroutine
    """

    no_auth_routes = filter(lambda _route: _route.path in no_auth_endpoints, all_routes)
    for route in no_auth_routes:
        has_auth = lookup_auth_dependency(route, auth_coro)
        assert not has_auth, f"Route protected: {route.path}"


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
        "/metrics",
        "/saml/sso/",
        "/graphql",
        "/graphql/",
        # Testing endpoints are not available in deployments
        "/testing/amqp/emit",
        "/testing/database/snapshot",
        "/testing/database/restore",
        # LoRa endpoints are only available on localhost
        "/lora/",
        "/lora/klassifikation/classes",
        "/lora/klassifikation/facet",
        "/lora/klassifikation/facet/fields",
        "/lora/klassifikation/facet/schema",
        "/lora/klassifikation/facet/{uuid}",
        "/lora/klassifikation/klasse",
        "/lora/klassifikation/klasse/fields",
        "/lora/klassifikation/klasse/schema",
        "/lora/klassifikation/klasse/{uuid}",
        "/lora/klassifikation/klassifikation",
        "/lora/klassifikation/klassifikation/fields",
        "/lora/klassifikation/klassifikation/schema",
        "/lora/klassifikation/klassifikation/{uuid}",
        "/lora/organisation/bruger",
        "/lora/organisation/bruger/fields",
        "/lora/organisation/bruger/schema",
        "/lora/organisation/bruger/{uuid}",
        "/lora/organisation/classes",
        "/lora/organisation/itsystem",
        "/lora/organisation/itsystem/fields",
        "/lora/organisation/itsystem/schema",
        "/lora/organisation/itsystem/{uuid}",
        "/lora/organisation/organisation",
        "/lora/organisation/organisation/fields",
        "/lora/organisation/organisation/schema",
        "/lora/organisation/organisation/{uuid}",
        "/lora/organisation/organisationenhed",
        "/lora/organisation/organisationenhed/fields",
        "/lora/organisation/organisationenhed/schema",
        "/lora/organisation/organisationenhed/{uuid}",
        "/lora/organisation/organisationfunktion",
        "/lora/organisation/organisationfunktion/fields",
        "/lora/organisation/organisationfunktion/schema",
        "/lora/organisation/organisationfunktion/{uuid}",
        "/lora/site-map",
    }
    yield no_auth_endpoints


@pytest.fixture
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
@pytest.mark.usefixtures("empty_db")
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
@pytest.mark.usefixtures("empty_db")
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_no_auth_graphql(raw_client: TestClient, latest_graphql_url: str) -> None:
    response = raw_client.post(latest_graphql_url, json={"query": "{ org { uuid } }"})
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
@pytest.mark.usefixtures("fixture_db")
def test_auth_service_org(
    admin_client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = admin_client.get("/service/o/", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_auth_graphql(
    raw_client: TestClient,
    auth_headers: dict[str, str],
    latest_graphql_url: str,
) -> None:
    response = raw_client.post(
        latest_graphql_url,
        headers=auth_headers,
        json={"query": "{ org { uuid } }"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"}}
    }


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_parsed_correctly_uuid():
    token = Token(azp="mo-frontend", uuid="30c89ad2-e0bb-42ae-82a8-1ae36943cb9e")
    assert token.uuid == UUID("30c89ad2-e0bb-42ae-82a8-1ae36943cb9e")


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_parsed_correctly_base64():
    token = Token(azp="mo-frontend", uuid="0prIMLvgrkKCqBrjaUPLng==")

    assert token.uuid == UUID("30c89ad2-e0bb-42ae-82a8-1ae36943cb9e")


@util.override_config(Settings(keycloak_rbac_enabled=True))
def test_uuid_parse_fails_on_garbage():
    with pytest.raises(ValidationError) as err:
        Token(
            azp="mo-frontend",
            realm_access=RealmAccess(roles={"owner"}),
            uuid="garbageasdasd",
        )
    errors = err.value.errors()[0]

    assert errors["msg"] == "value is not a valid uuid"
    assert errors["type"] == "type_error.uuid"
    assert len(err.value.errors()) == 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_missing_service_api_access(
    raw_client: TestClient,
) -> None:
    app = raw_client.app

    # Switch to a user without ServiceAPI permission
    app.dependency_overrides[auth] = serviceapiless_auth

    # Make call to random endpoint
    response = raw_client.get("/service/o/")
    assert response.status_code == 403
    assert response.json() == {"status": "Forbidden", "msg": "The Service API is gone"}

    # Switch to a user with ServiceAPI permission
    app.dependency_overrides[auth] = fake_auth

    # Make call to random endpoint
    response = raw_client.get("/service/o/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        }
    ]
