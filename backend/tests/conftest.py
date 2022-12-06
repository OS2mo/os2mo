# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import os
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Generator
from dataclasses import dataclass
from operator import itemgetter
from typing import Any
from typing import TypeVar
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import psycopg2
import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis import Verbosity
from hypothesis.database import InMemoryExampleDatabase
from more_itertools import last
from more_itertools import one
from respx.mocks import HTTPCoreMocker
from starlette_context import context
from starlette_context import request_cycle_context

from mora import lora
from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import Token
from mora.auth.keycloak.oidc import token_getter
from mora.auth.middleware import fetch_authenticated_user
from mora.config import get_settings
from mora.graphapi.main import graphql_versions
from mora.graphapi.versions.latest.dataloaders import MOModel
from mora.graphapi.versions.latest.models import NonEmptyString
from mora.service.org import ConfiguredOrganisation
from oio_rest.db import get_connection
from oio_rest.db.testing import ensure_testing_database_exists
from ramodels.mo import Validity
from tests.hypothesis_utils import validity_model_strat
from tests.util import _mox_testing_api
from tests.util import darmock
from tests.util import load_sample_structures
from tests.util import MockAioresponses


T = TypeVar("T")
YieldFixture = Generator[T, None, None]


# Configs + fixtures
h_db = InMemoryExampleDatabase()
h_settings.register_profile("ci", max_examples=30, deadline=None, database=h_db)
h_settings.register_profile("dev", max_examples=10, deadline=None, database=h_db)
h_settings.register_profile(
    "debug", max_examples=10, verbosity=Verbosity.verbose, database=h_db
)
h_settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))

asyncio_mode = "strict"


@pytest.fixture(autouse=True, scope="session")
def seed_lora_client() -> None:
    os.environ["PYTEST_RUNNING"] = "True"
    lora.client = asyncio.run(lora.create_lora_client(create_app()))


def pytest_runtest_protocol(item) -> None:
    os.environ["PYTEST_RUNNING"] = "True"


st.register_type_strategy(Validity, validity_model_strat())


@pytest.fixture(autouse=True)
def clear_configured_organisation():
    ConfiguredOrganisation.clear()


@pytest.fixture(scope="class")
def mock_asgi_transport() -> YieldFixture[None]:
    HTTPCoreMocker.add_targets(
        "httpx._transports.asgi.ASGITransport",
        "httpx._transports.wsgi.WSGITransport",
    )
    yield
    HTTPCoreMocker.remove_targets(
        "httpx._transports.asgi.ASGITransport",
        "httpx._transports.wsgi.WSGITransport",
    )


@pytest.fixture()
def set_settings(
    monkeypatch: MonkeyPatch,
) -> YieldFixture[Callable[..., None]]:
    """Set settings via kwargs callback."""

    def _inner(**kwargs: Any) -> None:
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield _inner
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def mocked_context():
    """
    Testing code that relies on context vars without a full test client / app.
    https://starlette-context.readthedocs.io/en/latest/testing.html
    """
    context_store = {}
    with request_cycle_context(context_store):
        yield context


async def fake_auth() -> Token:
    return Token(
        azp="vue",
        email="bruce@kung.fu",
        preferred_username="bruce",
        realm_access={"roles": set()},
        uuid="99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
    )


async def admin_auth() -> Token:
    auth = await fake_auth()
    auth.realm_access.roles = {"admin"}
    return auth


async def admin_auth_uuid() -> UUID:
    token = await admin_auth()
    return token.uuid


def fake_token_getter() -> Callable[[], Awaitable[Token]]:
    async def get_fake_token():
        token = await fake_auth()
        return token

    return get_fake_token


def admin_token_getter() -> Callable[[], Awaitable[Token]]:
    async def get_fake_admin_token():
        token = await admin_auth()
        return token

    return get_fake_admin_token


def raw_test_app(**overrides: Any) -> FastAPI:
    app = create_app(overrides)
    return app


def test_app(**overrides: Any) -> FastAPI:
    app = raw_test_app(**overrides)
    app.dependency_overrides[auth] = fake_auth
    app.dependency_overrides[token_getter] = fake_token_getter
    return app


def admin_test_app(**overrides: Any) -> FastAPI:
    app = raw_test_app(**overrides)
    app.dependency_overrides[auth] = admin_auth
    app.dependency_overrides[fetch_authenticated_user] = admin_auth_uuid
    app.dependency_overrides[token_getter] = admin_token_getter
    return app


@pytest.fixture(scope="session")
def fastapi_raw_test_app() -> FastAPI:
    return raw_test_app()


@pytest.fixture(scope="session")
def fastapi_test_app() -> FastAPI:
    return test_app()


@pytest.fixture(scope="session")
def fastapi_admin_test_app() -> FastAPI:
    return admin_test_app()


def get_latest_graphql_url() -> str:
    """Return the latest GraphQL endpoint URL.

    This is defined in a separate function to allow usage from old
    unittest.TestCase classes.
    """
    latest = last(graphql_versions)
    return f"/graphql/v{latest.version}"


@pytest.fixture(scope="session")
def latest_graphql_url() -> str:
    return get_latest_graphql_url()


@pytest.fixture(scope="session")
def raw_client(fastapi_raw_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_raw_test_app) as client:
        yield client


@pytest.fixture(scope="session")
def service_client(fastapi_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_test_app) as client:
        yield client


@pytest.fixture(scope="class")
def admin_client(fastapi_admin_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_admin_test_app) as client:
        yield client


@pytest.fixture(scope="class")
def testing_db() -> YieldFixture[None]:
    _mox_testing_api("db-setup")
    yield
    _mox_testing_api("db-teardown")


# Due to the current tight coupling between our unit and integration test,
# The load_fixture_data can not be set as a session
# scoped fixture with autouse true. Session fixture can not be
# used as an input to default/function scoped fixture.
are_fixtures_loaded = False


async def load_fixture_data() -> None:
    """Loads full sample structure
    Also naively looks if some of the sample structures are loaded
    to avoid loading all sample data more than once.
    """
    global are_fixtures_loaded
    if not are_fixtures_loaded:
        ensure_testing_database_exists()
        conn = get_connection()
        await load_sample_structures()
        conn.commit()  # commit the initial sample structures
        are_fixtures_loaded = True


@pytest.fixture(scope="class")
async def load_fixture_data_with_class_reset() -> YieldFixture[None]:

    await load_fixture_data()

    conn = get_connection()
    try:
        conn.set_session(autocommit=False)
    except psycopg2.ProgrammingError:
        conn.rollback()  # If a transaction is already in progress roll it back
        conn.set_session(autocommit=False)

    yield

    conn.rollback()


@pytest.fixture(scope="function")
async def load_fixture_data_with_reset() -> YieldFixture[None]:

    await load_fixture_data()

    conn = get_connection()
    try:
        conn.set_session(autocommit=False)
    except psycopg2.ProgrammingError:
        conn.rollback()  # If a transaction is already in progress roll it back
        conn.set_session(autocommit=False)

    yield

    conn.rollback()


@pytest.fixture(scope="session")
def event_loop() -> YieldFixture[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def sample_structures_minimal(testing_db) -> YieldFixture[None]:
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=True)
    yield
    _mox_testing_api("db-reset")


@pytest.fixture(scope="session")
def service_client_not_raising(fastapi_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_test_app, raise_server_exceptions=False) as client:
        yield client


@dataclass
class GQLResponse:
    data: dict | None
    errors: list[dict] | None
    status_code: int


@pytest.fixture(scope="class")
def graphapi_post(admin_client: TestClient, latest_graphql_url: str):
    def _post(
        query: str,
        variables: dict[str, Any] | None = None,
        url: str = latest_graphql_url,
    ) -> GQLResponse:
        response = admin_client.post(url, json={"query": query, "variables": variables})
        data, errors = response.json().get("data"), response.json().get("errors")
        status_code = response.status_code
        return GQLResponse(data=data, errors=errors, status_code=status_code)

    yield _post


@dataclass
class ServiceAPIResponse:
    data: dict | None
    status_code: int | None
    errors: list[Any] | None


@pytest.fixture(scope="session")
def serviceapi_post(service_client: TestClient):
    def _post(
        url: str,
        variables: dict[str, Any] | None = None,
        method: str = "get",
    ) -> ServiceAPIResponse:
        try:
            match (method.lower()):
                case "get":
                    response = service_client.get(url, json=variables)
                case "post":
                    response = service_client.post(url, json=variables)
                case _:
                    response = None

            if not response:
                return None

            return ServiceAPIResponse(
                status_code=response.status_code, data=response.json(), errors=None
            )
        except Exception as e:
            return ServiceAPIResponse(status_code=None, data=None, errors=[e])

    yield _post


def gen_organisation(
    uuid: UUID | None = None,
    name: str = "name",
    user_key: str = "user_key",
) -> dict[str, Any]:
    uuid = uuid or uuid4()
    organisation = {
        "id": str(uuid),
        "registreringer": [
            {
                "attributter": {
                    "organisationegenskaber": [
                        {
                            "brugervendtnoegle": user_key,
                            "organisationsnavn": name,
                        }
                    ]
                },
                "tilstande": {"organisationgyldighed": [{"gyldighed": "Aktiv"}]},
            }
        ],
    }
    return organisation


@pytest.fixture
def mock_organisation(respx_mock) -> YieldFixture[UUID]:
    organisation = gen_organisation()

    respx_mock.get(
        "http://localhost/lora/organisation/organisation",
    ).mock(return_value=Response(200, json={"results": [[organisation]]}))
    return organisation["id"]


@pytest.fixture
def mock_get_valid_organisations(respx_mock) -> YieldFixture[UUID]:
    organisation = gen_organisation()

    reg = one(organisation["registreringer"])
    attrs = one(reg["attributter"]["organisationegenskaber"])
    mocked_organisation = {
        "name": attrs["organisationsnavn"],
        "user_key": attrs["brugervendtnoegle"],
        "uuid": organisation["id"],
    }
    with patch("mora.service.org.get_valid_organisations") as mock:
        mock.return_value = [mocked_organisation]
        yield UUID(mocked_organisation["uuid"])


st.register_type_strategy(NonEmptyString, st.text(min_size=1))


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


@pytest.fixture(scope="session")
def graphapi_test(fastapi_admin_test_app: FastAPI) -> TestClient:
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    return TestClient(fastapi_admin_test_app)


@pytest.fixture(scope="session")
def graphapi_test_no_exc(fastapi_admin_test_app: FastAPI) -> TestClient:
    """Fixture yielding a FastAPI test client.

    This test client does not raise server errors. We use it to check error handling
    in our GraphQL stack.
    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    return TestClient(fastapi_admin_test_app, raise_server_exceptions=False)


@pytest.fixture
def darmocked():
    with darmock() as mock:
        yield mock


@pytest.fixture
def mockaio():
    with MockAioresponses(["dawa-autocomplete.json"]) as mock:
        yield mock


def get_keycloak_token(use_client_secret: bool = False) -> str:
    """Get OIDC token from Keycloak to send to MOs backend.

    Args:
        use_client_secret: Whether to use client_secret or password.

    Returns:
        Encoded OIDC token from Keycloak
    """

    data = {
        "grant_type": "password",
        "client_id": "mo",
        "username": "bruce",
        "password": "bruce",
    }
    if use_client_secret:
        data = {
            "grant_type": "client_credentials",
            "client_id": "dipex",
            "client_secret": "603f1c82-d012-4d04-9382-dbe659c533fb",
        }

    r = requests.post(
        "http://keycloak:8080/auth/realms/mo/protocol/openid-connect/token",
        data=data,
    )
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def token():
    return get_keycloak_token()


@pytest.fixture(scope="session")
def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}
