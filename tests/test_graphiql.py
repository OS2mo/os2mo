# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mora.graphapi.custom_router import DEPRECATION_NOTICE
from mora.graphapi.version import LATEST_VERSION

GRAPHIQL_DEPRECATION_NOTICE = DEPRECATION_NOTICE.replace("__LATEST_URL__", "/graphql")
APOLLO_SANDBOX_DEPRECATION_NOTICE = DEPRECATION_NOTICE.replace(
    "__LATEST_URL__", "/graphql/apollo-sandbox"
)


@pytest.mark.parametrize(
    "url,deprecated",
    [
        ("/graphql", False),
        ("/graphql/v21", True),
        ("/graphql/v22", True),
        ("/graphql/v23", True),
        ("/graphql/v24", True),
        ("/graphql/v25", True),
        ("/graphql/v26", True),
        ("/graphql/v27", True),
        ("/graphql/v28", True),
        ("/graphql/v29", True),
        ("/graphql/v30", False),
    ],
)
def test_graphiql_overrides(
    service_client: TestClient, url: str, deprecated: bool
) -> None:
    response = service_client.request("GET", url)
    assert response.status_code == 200
    html_response = response.text
    if deprecated:
        assert GRAPHIQL_DEPRECATION_NOTICE in html_response
    else:
        assert GRAPHIQL_DEPRECATION_NOTICE not in html_response


@pytest.mark.parametrize(
    "url,deprecated",
    [
        ("/graphql/apollo-sandbox", False),
        ("/graphql/v21/apollo-sandbox", True),
        ("/graphql/v22/apollo-sandbox", True),
        ("/graphql/v23/apollo-sandbox", True),
        ("/graphql/v24/apollo-sandbox", True),
        ("/graphql/v25/apollo-sandbox", True),
        ("/graphql/v26/apollo-sandbox", True),
        ("/graphql/v27/apollo-sandbox", True),
        ("/graphql/v28/apollo-sandbox", True),
        ("/graphql/v29/apollo-sandbox", True),
        ("/graphql/v30/apollo-sandbox", False),
    ],
)
def test_apollo_sandbox_overrides(
    service_client: TestClient, url: str, deprecated: bool
) -> None:
    response = service_client.request("GET", url)
    assert response.status_code == 200
    html_response = response.text
    if deprecated:
        assert APOLLO_SANDBOX_DEPRECATION_NOTICE in html_response
    else:
        assert APOLLO_SANDBOX_DEPRECATION_NOTICE not in html_response


def test_apollo_sandbox_redirects_to_latest(service_client: TestClient) -> None:
    response = service_client.request(
        "GET", "/graphql/apollo-sandbox", follow_redirects=False
    )
    assert response.status_code == 307
    assert (
        response.headers["location"]
        == f"/graphql/v{LATEST_VERSION.value}/apollo-sandbox"
    )


@pytest.mark.parametrize(
    "path,headers",
    [
        ("", {"Accept": "text/html"}),
        ("/apollo-sandbox", {}),
    ],
)
def test_ide_injects_keycloak_config(
    fastapi_test_app: FastAPI,
    service_client: TestClient,
    path: str,
    headers: dict[str, str],
) -> None:
    response = service_client.request("GET", f"/graphql/v29{path}", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html_response = response.text
    settings = fastapi_test_app.state.settings
    assert f'url: "{settings.keycloak_auth_server_url}"' in html_response
    assert f'realm: "{settings.keycloak_realm}"' in html_response
    assert f'clientId: "{settings.keycloak_mo_client}"' in html_response
    assert "__KEYCLOAK" not in html_response
    assert "__GRAPHQL_ENDPOINT__" not in html_response
    assert "__LATEST_URL__" not in html_response


def test_apollo_sandbox_endpoint(service_client: TestClient) -> None:
    response = service_client.request("GET", "/graphql/v29/apollo-sandbox")
    assert response.status_code == 200
    assert 'new URL("/graphql/v29", window.location.origin)' in response.text
