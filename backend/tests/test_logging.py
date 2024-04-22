# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY

import pytest
from fastapi import Depends
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware
from structlog.testing import capture_logs

from .conftest import fake_auth
from .conftest import fake_token_getter
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import token_getter
from mora.auth.middleware import set_authenticated_user
from mora.log import gen_request_logging_dependency
from mora.log import request_id_dependency


@pytest.fixture
async def minimal_logging_app() -> FastAPI:
    app = FastAPI(
        middleware=[
            Middleware(RawContextMiddleware),
        ],
        dependencies=[
            Depends(set_authenticated_user),
            Depends(request_id_dependency),
            Depends(gen_request_logging_dependency()),
        ],
    )

    @app.get("/")
    def index() -> dict[str, str]:
        return {"hello": "world"}

    @app.get("/authed")
    def authed(token: Token = Depends(auth)) -> dict[str, str]:
        return {"hello": str(token.email)}

    return app


async def test_access_log_middleware_minimal(minimal_logging_app: FastAPI) -> None:
    with TestClient(minimal_logging_app) as client:
        with capture_logs() as cap_logs:
            response = client.get("/")
            assert response.status_code == 200
            assert response.json() == {"hello": "world"}

    assert cap_logs == [
        {
            "actor": "05211100-baad-1110-006e-6f2075756964",
            "duration": ANY,
            "event": "Request",
            "log_level": "info",
            "method": "GET",
            "network": {"client": {"ip": "testclient", "port": 50000}},
            "path": "/",
        }
    ]


async def test_access_log_middleware_auth_override(
    minimal_logging_app: FastAPI,
) -> None:
    minimal_logging_app.dependency_overrides[auth] = fake_auth
    minimal_logging_app.dependency_overrides[token_getter] = fake_token_getter

    with TestClient(minimal_logging_app) as client:
        with capture_logs() as cap_logs:
            response = client.get("/authed")
            assert response.status_code == 200
            assert response.json() == {"hello": "bruce@kung.fu"}

    assert cap_logs == [
        {
            "actor": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
            "duration": ANY,
            "event": "Request",
            "log_level": "info",
            "method": "GET",
            "network": {"client": {"ip": "testclient", "port": 50000}},
            "path": "/authed",
        }
    ]


async def test_access_log_middleware_raw_client(raw_client: TestClient) -> None:
    with capture_logs() as cap_logs:
        response = raw_client.get("/version/")
        assert response.status_code == 200

    assert cap_logs == [
        {
            "actor": "05211100-baad-1110-006e-6f2075756964",
            "duration": ANY,
            "event": "Request",
            "log_level": "info",
            "method": "GET",
            "network": {"client": {"ip": "testclient", "port": 50000}},
            "path": "/version/",
        }
    ]


async def test_access_log_middleware_admin_client(admin_client: TestClient) -> None:
    with capture_logs() as cap_logs:
        response = admin_client.get("/version/")
        assert response.status_code == 200

    assert cap_logs == [
        {
            "actor": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
            "duration": ANY,
            "event": "Request",
            "log_level": "info",
            "method": "GET",
            "network": {"client": {"ip": "testclient", "port": 50000}},
            "path": "/version/",
        }
    ]
