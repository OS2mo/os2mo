# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pytest configurations for GraphAPI tests.

This file specifies different pytest fixtures and settings shared throughout the
GraphAPI test suite. Some are autoused for each test invocation, while others are made
available for use as needed.
"""
from collections.abc import Awaitable
from collections.abc import Callable
from operator import itemgetter
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import Token
from mora.auth.keycloak.oidc import token_getter
from mora.auth.middleware import fetch_authenticated_user
from mora.graphapi.versions.latest.dataloaders import get_loaders
from mora.graphapi.versions.latest.dataloaders import MOModel
from mora.graphapi.versions.latest.version import LatestGraphQLSchema
from tests.conftest import fake_auth
from tests.conftest import GQLResponse


@pytest.fixture(scope="class")
def patch_loader():
    """Fixture to patch dataloaders for mocks.

    It looks a little weird, being a function yielding a function which returns
    a function. However, this is necessary in order to be able to use the fixture
    with extra parameters.
    """

    def patcher(data: list[MOModel]):
        # If our dataloader functions were sync, we could have used a lambda directly
        # when monkeypatching. They are async, however, and as such we need to mock
        # using an async function.
        async def _patcher(*args, **kwargs):
            return data

        return _patcher

    yield patcher


async def admin_auth():
    auth = await fake_auth()
    auth.update(
        {
            "realm_access": {
                "roles": {
                    "admin",
                }
            }
        }
    )
    return Token(**auth)


async def admin_auth_uuid():
    token = await admin_auth()
    return token.uuid


def admin_token_getter() -> Callable[[], Awaitable[Token]]:
    async def get_fake_admin_token():
        token = await admin_auth()
        return token

    return get_fake_admin_token


graph_app = None


def test_app():
    global graph_app
    if not graph_app:
        graph_app = create_app()
        graph_app.dependency_overrides[auth] = admin_auth
        graph_app.dependency_overrides[fetch_authenticated_user] = admin_auth_uuid
        graph_app.dependency_overrides[token_getter] = admin_token_getter
    return graph_app


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

    async def _execute(query: str, values: dict | None = None):
        schema = LatestGraphQLSchema.get()
        loaders = await get_loaders()
        result = await schema.execute(
            query, variable_values=values, context_value=loaders
        )
        return result

    yield _execute


@pytest.fixture(scope="class", name="org_uuids")
def fetch_org_uuids(
    load_fixture_data_with_class_reset, graphapi_post: Callable
) -> list[UUID]:
    parent_uuids_query = """
        query FetchOrgUUIDs {
            org_units {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(parent_uuids_query)
    assert response.errors is None
    uuids = list(map(UUID, map(itemgetter("uuid"), response.data["org_units"])))
    return uuids


@pytest.fixture(scope="class", name="employee_uuids")
def fetch_employee_uuids(
    load_fixture_data_with_class_reset, graphapi_post: Callable
) -> list[UUID]:
    parent_uuids_query = """
        query FetchEmployeeUUIDs {
            employees {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(parent_uuids_query)
    assert response.errors is None
    uuids = list(map(UUID, map(itemgetter("uuid"), response.data["employees"])))
    return uuids


@pytest.fixture(scope="class", name="itsystem_uuids")
def fetch_itsystem_uuids(
    load_fixture_data_with_class_reset, graphapi_post: Callable
) -> list[UUID]:
    itsystem_uuids_query = """
        query FetchITSystemUUIDs {
            itsystems {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(itsystem_uuids_query)
    assert response.errors is None
    uuids = list(map(UUID, map(itemgetter("uuid"), response.data["itsystems"])))
    return uuids
