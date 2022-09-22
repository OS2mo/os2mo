# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import GQLResponse
from tests.conftest import test_app


@pytest.fixture
def graphapi_test():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(test_app(graphql_enable=True)) as client:
        yield client


@pytest.fixture
def graphapi_post_integration(graphapi_test: TestClient):
    def _post(query: str, variables: dict[str, Any] | None = None) -> GQLResponse:
        response = graphapi_test.post(
            "/graphql", json={"query": query, "variables": variables}
        )
        data, errors = response.json().get("data"), response.json().get("errors")
        status_code = response.status_code
        return GQLResponse(data=data, errors=errors, status_code=status_code)

    yield _post
