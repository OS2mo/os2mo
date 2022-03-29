#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from collections import namedtuple
from typing import Any
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from tests.cases import fake_auth

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


def test_app(**overrides: Any):
    app = create_app(overrides)
    app.dependency_overrides[auth] = fake_auth
    return app


@pytest.fixture
def service_client():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(test_app()) as client:
        yield client


@pytest.fixture(scope="class")
def graphapi_test():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(test_app(graphql_enable=True)) as client:
        yield client


GQLResponse = namedtuple("GQLResponse", ["data", "errors", "status_code"])


@pytest.fixture(scope="class")
def graphapi_post(graphapi_test: TestClient):
    def _post(query: str, variables: Optional[dict[str, Any]] = None) -> GQLResponse:
        response = graphapi_test.post(
            "/graphql", json={"query": query, "variables": variables}
        )
        data, errors = response.json().get("data"), response.json().get("errors")
        status_code = response.status_code
        return GQLResponse(data=data, errors=errors, status_code=status_code)

    yield _post
