# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pytest configurations for GraphAPI tests.

This file specifies different pytest fixtures and settings shared throughout the
GraphAPI test suite. Some are autoused for each test invocation, while others are made
available for use as needed.
"""
from typing import List
from typing import Optional

import pytest
from fastapi.testclient import TestClient

from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from mora.graphapi.versions.latest.dataloaders import get_loaders
from mora.graphapi.versions.latest.dataloaders import MOModel
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from tests.conftest import fake_auth


@pytest.fixture(scope="class")
def patch_loader():
    """Fixture to patch dataloaders for mocks.

    It looks a little weird, being a function yielding a function which returns
    a function. However, this is necessary in order to be able to use the fixture
    with extra parameters.
    """

    def patcher(data: List[MOModel]):
        # If our dataloader functions were sync, we could have used a lambda directly
        # when monkeypatching. They are async, however, and as such we need to mock
        # using an async function.
        async def _patcher(*args, **kwargs):
            return data

        return _patcher

    yield patcher


async def admin_auth():
    auth = await fake_auth()
    auth.update({"realm_access": {"roles": "admin"}})
    return auth


def test_app():
    app = create_app(settings_overrides={"graphql_enable": True})
    app.dependency_overrides[auth] = admin_auth
    return app


@pytest.fixture(scope="class")
def graphapi_test():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    yield TestClient(test_app())


@pytest.fixture(scope="class")
def graphapi_test_no_exc():
    """Fixture yielding a FastAPI test client.

    This test client does not raise server errors. We use it to check error handling
    in our GraphQL stack.
    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    yield TestClient(test_app(), raise_server_exceptions=False)


@pytest.fixture(scope="class")
def execute():
    """Fixture to execute queries, optionally with values, against our GraphQL schema.

    If dataloaders are mocked, this should always be called within the same context,
    but *after* the actual mock. Otherwise, the loaders context value will not
    pick up the mock correctly.
    """

    async def _execute(query: str, values: Optional[dict] = None):
        schema = LatestGraphQLSchema.get()
        loaders = await get_loaders()
        result = await schema.execute(
            query, variable_values=values, context_value=loaders
        )
        return result

    yield _execute
