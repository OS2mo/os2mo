# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import os
from collections.abc import Callable
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any
from uuid import UUID
from uuid import uuid4

import psycopg2
import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis import Verbosity
from hypothesis.database import InMemoryExampleDatabase
from respx.mocks import HTTPCoreMocker
from starlette_context import _request_scope_context_storage
from starlette_context.ctx import _Context

from mora import lora
from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from mora.config import get_settings
from mora.graphapi.versions.latest.models import NonEmptyString
from mora.service.org import ConfiguredOrganisation
from oio_rest.db import get_connection
from oio_rest.db.testing import ensure_testing_database_exists
from ramodels.mo import Validity
from tests.hypothesis_utils import validity_model_strat
from tests.util import _mox_testing_api
from tests.util import load_sample_structures

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
def seed_lora_client():
    os.environ["PYTEST_RUNNING"] = "True"
    lora.client = asyncio.run(lora.create_lora_client(create_app()))


def pytest_runtest_protocol(item):
    os.environ["PYTEST_RUNNING"] = "True"
    if item.get_closest_marker("integration_test"):
        if item.get_closest_marker("slow"):
            item.add_marker(pytest.mark.execution_timeout(80))
        else:
            item.add_marker(pytest.mark.execution_timeout(3))
        # Using 'are_fixtures_loaded' ensures that the timout is not applied
        # when creating the first instance of the sample_structures
        global are_fixtures_loaded
        if are_fixtures_loaded and not item.get_closest_marker("slow_setup"):
            item.add_marker(pytest.mark.setup_timeout(2.0))


st.register_type_strategy(Validity, validity_model_strat())


@pytest.fixture(scope="class")
def mock_asgi_transport():
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
) -> Generator[Callable[..., None], None, None]:
    """Set settings via kwargs callback."""

    def _inner(**kwargs: Any) -> None:
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield _inner
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def mocked_context(monkeypatch) -> _Context:
    """
    Testing code that relies on context vars without a full test client / app.
    Originally inspired by this solution from the author of starlette-context:
    https://github.com/tomwojcik/starlette-context/issues/46#issuecomment-867148272.
    """

    @property
    def data(self) -> dict:
        """
        The original _Context.data method, but returns an empty dict on error.
        """
        try:
            return _request_scope_context_storage.get()
        except LookupError:
            return {}

    monkeypatch.setattr(_Context, "data", data)
    return _Context()


async def fake_auth():
    return {
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
        "uuid": "99e7b256-7dfa-4ee8-95c6-e3abe82e236a",
    }


def test_app(**overrides: Any):
    app = create_app(overrides)
    app.dependency_overrides[auth] = fake_auth
    return app


@pytest.fixture(scope="class")
def fastapi_test_app():
    yield test_app()


@pytest.fixture
def service_client(fastapi_test_app):
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_test_app) as client:
        yield client


@pytest.fixture(scope="class")
def testing_db():
    _mox_testing_api("db-setup")
    yield
    _mox_testing_api("db-teardown")


# Due to the current tight coupling between our unit and integration test,
# The load_fixture_data can not be set as a session
# scoped fixture with autouse true. Session fixture can not be
# used as an input to default/function scoped fixture.
are_fixtures_loaded = False


async def load_fixture_data():
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
async def load_fixture_data_with_class_reset():

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
async def load_fixture_data_with_reset():

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
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def sample_structures_minimal(testing_db):
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=True)
    yield
    _mox_testing_api("db-reset")


@pytest.fixture()
def service_client_not_raising(fastapi_test_app):
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
def graphapi_post(graphapi_test: TestClient):
    def _post(
        query: str, variables: dict[str, Any] | None = None, url: str = "/graphql"
    ) -> GQLResponse:
        with graphapi_test as client:
            response = client.post(url, json={"query": query, "variables": variables})
        data, errors = response.json().get("data"), response.json().get("errors")
        status_code = response.status_code
        return GQLResponse(data=data, errors=errors, status_code=status_code)

    yield _post


@dataclass
class ServiceAPIResponse:
    data: dict | None
    status_code: int | None
    errors: list[Any] | None


@pytest.fixture(scope="class")
def serviceapi_test():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    yield TestClient(test_app())


@pytest.fixture(scope="class")
def serviceapi_post(serviceapi_test: TestClient):
    def _post(
        url: str,
        variables: dict[str, Any] | None = None,
        method: str = "get",
    ) -> ServiceAPIResponse:
        try:
            with serviceapi_test as client:
                match (method.lower()):
                    case "get":
                        response = client.get(url, json=variables)
                    case "post":
                        response = client.post(url, json=variables)
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
def mock_organisation(respx_mock) -> Generator[UUID, None, None]:
    # Clear Organisation cache before mocking a new one
    ConfiguredOrganisation.clear()

    organisation = gen_organisation()

    respx_mock.get(
        "http://localhost/lora/organisation/organisation",
    ).mock(return_value=Response(200, json={"results": [[organisation]]}))
    yield organisation["id"]


st.register_type_strategy(NonEmptyString, st.text(min_size=1))
