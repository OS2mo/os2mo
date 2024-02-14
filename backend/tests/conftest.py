# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import os
from collections.abc import AsyncGenerator
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from operator import itemgetter
from typing import Any
from typing import Protocol
from typing import TypeVar
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import psycopg2
import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis import Verbosity
from hypothesis.database import InMemoryExampleDatabase
from more_itertools import last
from more_itertools import one
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_context import request_cycle_context

from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import Token
from mora.auth.keycloak.oidc import token_getter
from mora.auth.middleware import fetch_authenticated_user
from mora.config import get_settings
from mora.db import create_sessionmaker as mo_create_sessionmaker
from mora.graphapi.main import graphql_versions
from mora.graphapi.versions.latest.dataloaders import MOModel
from mora.graphapi.versions.latest.permissions import ALL_PERMISSIONS
from mora.service.org import ConfiguredOrganisation
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.db import _get_dbname
from oio_rest.db import dbname_context
from oio_rest.db import get_connection
from oio_rest.organisation import Organisation
from ramodels.mo import Validity
from tests.db_testing import create_new_testing_database
from tests.db_testing import remove_testing_database
from tests.db_testing import reset_testing_database
from tests.db_testing import setup_testing_database
from tests.hypothesis_utils import validity_model_strat
from tests.util import darmock
from tests.util import load_sample_structures
from tests.util import MockAioresponses

T = TypeVar("T")
YieldFixture = Generator[T, None, None]
AsyncYieldFixture = AsyncGenerator[T, None]


# Configs + fixtures
h_db = InMemoryExampleDatabase()
h_settings.register_profile("ci", max_examples=30, deadline=None, database=h_db)
h_settings.register_profile("dev", max_examples=10, deadline=None, database=h_db)
h_settings.register_profile(
    "debug", max_examples=10, verbosity=Verbosity.verbose, database=h_db
)
h_settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))

asyncio_mode = "strict"


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.respx(using="httpx"))


def pytest_runtest_protocol(item) -> None:
    os.environ["TESTING"] = "True"
    os.environ["PYTEST_RUNNING"] = "True"


st.register_type_strategy(Validity, validity_model_strat())


@pytest.fixture(autouse=True)
def clear_configured_organisation():
    ConfiguredOrganisation.clear()


@pytest.fixture
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


@pytest.fixture(scope="session")
def monkeysession(request):
    from pytest import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def set_session_settings(
    monkeysession: MonkeyPatch,
) -> YieldFixture[Callable[..., None]]:
    """Set settings via kwargs callback."""

    def _inner(**kwargs: Any) -> None:
        for key, value in kwargs.items():
            monkeysession.setenv(key, value)
        get_settings.cache_clear()

    yield _inner
    get_settings.cache_clear()


@pytest.fixture(autouse=True, scope="session")
async def mocked_context() -> YieldFixture[None]:
    """
    Testing code that relies on context vars without a full test client / app.
    https://starlette-context.readthedocs.io/en/latest/testing.html
    """
    # NOTE: This fixture MUST be async to ensure the context is propagated correctly
    # to the tests.
    assert asyncio.get_running_loop()
    with request_cycle_context({}):
        yield


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
    auth.realm_access.roles = {"admin", "owner"}.union(ALL_PERMISSIONS)
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


@pytest.fixture(scope="session")
def fastapi_session_test_app(
    fastapi_test_app: FastAPI,
    fixture_db: str,
) -> FastAPI:
    lora_settings = lora_get_settings()
    fastapi_test_app.state.sessionmaker = create_sessionmaker(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=fixture_db,
    )
    return fastapi_test_app


@pytest.fixture(scope="session")
def latest_graphql_url() -> str:
    latest = last(graphql_versions)
    return f"/graphql/v{latest.version}"


@pytest.fixture(scope="session")
def raw_client(fastapi_raw_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    with TestClient(fastapi_raw_test_app) as client:
        yield client


@pytest.fixture(scope="session")
def service_client(fastapi_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    with TestClient(fastapi_test_app) as client:
        yield client


@pytest.fixture(scope="session")
def admin_client(fastapi_admin_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    with TestClient(fastapi_admin_test_app) as client:
        yield client


@pytest.fixture(scope="session")
def service_client_not_raising() -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    app = test_app()
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


@contextmanager
def create_test_database(identifier: str) -> YieldFixture[str]:
    new_db_name = create_new_testing_database(identifier)
    try:
        # Set dbname_context to ensure all coming database connections connect
        # to our new database instead of the 'mox' database.
        token = dbname_context.set(new_db_name)
        # Install "actual_state" schema in testing database
        setup_testing_database()
        yield new_db_name
        dbname_context.reset(token)
    finally:
        remove_testing_database(new_db_name)


@pytest.fixture(scope="session")
def testing_db() -> YieldFixture[str]:
    """Setup a new empty database.

    Yields:
        The newly created databases name.
    """
    with create_test_database("empty") as db_name:
        yield db_name


@pytest.fixture(scope="session")
def fixture_db() -> YieldFixture[str]:
    """Setup a new empty database.

    Yields:
        The newly created databases name.
    """
    with create_test_database("fixture") as db_name:
        yield db_name


@pytest.fixture(scope="session")
async def load_fixture(fixture_db: str) -> AsyncYieldFixture[str]:
    """Load our database fixture into an new database.

    Note:
        This function cannot be merged to `fixture_db` due to this function being
        async and `fixture_db` being a sync fixture.

    Yields:
        The newly created databases name.
    """
    conn = get_connection()
    await load_sample_structures()
    conn.commit()  # commit the initial sample structures
    yield fixture_db


@pytest.fixture
def empty_db(testing_db: str) -> YieldFixture[str]:
    """Ensure an empty testing database is available."""
    # Set dbname_context again, as we are just about to run a test,
    # and as it may be set to another testing database
    token = dbname_context.set(testing_db)
    reset_testing_database()
    try:
        yield testing_db
    finally:
        dbname_context.reset(token)


@pytest.fixture
def load_fixture_data_with_reset(load_fixture: None) -> YieldFixture[None]:
    """Ensure a fixture testing database is available. Run test inside transaction."""
    # Set dbname_context again, as we are just about to run a test,
    # and as it may be set to another testing database
    token = dbname_context.set(load_fixture)

    # Pre-seed the connection, disabling auto-commit on it.
    # Ensuring tests do not ruin our fixture database.
    conn = get_connection()
    try:
        conn.set_session(autocommit=False)
    except psycopg2.ProgrammingError:
        conn.rollback()  # If a transaction is already in progress roll it back
        conn.set_session(autocommit=False)

    try:
        yield
    finally:
        conn.rollback()
        dbname_context.reset(token)


@pytest.fixture
def event_loop() -> YieldFixture[asyncio.AbstractEventLoop]:
    """Custom implementation of pytest-asyncio's event_loop fixture[1].

    This fixture is used by pytest-asyncio to run test's setup/run/teardown. It
    is needed to share contextvars between these stages; without it,
    contextvars from async coroutine fixtures are not passed correctly to the
    individual tests. See the issue[2] with solution implementation[3].

    The fixture name shadows the default fixture from pytest-asyncio, and thus
    overrides it.

    [1] https://github.com/pytest-dev/pytest-asyncio/blob/e92efad68146469228b3ac3478b254b692c6bc90/pytest_asyncio/plugin.py#L957-L970
    [2] https://github.com/pytest-dev/pytest-asyncio/issues/127
    [3] https://github.com/Donate4Fun/donate4fun/blob/cdf047365b7d2df83a952f5bb9544c29051fbdbd/tests/fixtures.py#L87-L113
    """
    def task_factory(loop, coro, context=None):
        # The task_factory breaks context isolation for asyncio tasks, so we need to
        # check the calling context.
        stack = traceback.extract_stack()
        for frame in stack[-2::-1]:
            package_name = Path(frame.filename).parts[-2]
            if package_name != 'asyncio':
                if package_name == 'pytest_asyncio':
                    # This function was called from pytest_asyncio, use shared context
                    break
                else:
                    # This function was called from somewhere else, create context copy
                    context = None
                break
        return Task(coro, loop=loop, context=context)

    loop = asyncio.get_event_loop_policy().new_event_loop()
    context = contextvars.copy_context()

    loop.set_task_factory(partial(task_factory, context=context))
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@dataclass
class GQLResponse:
    data: dict | None
    errors: list[dict] | None
    extensions: dict | None
    status_code: int


class GraphAPIPost(Protocol):
    def __call__(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        url: str = latest_graphql_url,
    ) -> GQLResponse:
        ...


@pytest.fixture(scope="session")
def graphapi_post(admin_client: TestClient, latest_graphql_url: str) -> GraphAPIPost:
    def _post(
        query: str,
        variables: dict[str, Any] | None = None,
        url: str = latest_graphql_url,
    ) -> GQLResponse:
        response = admin_client.post(url, json={"query": query, "variables": variables})
        data = response.json().get("data")
        errors = response.json().get("errors")
        extensions = response.json().get("extensions")
        status_code = response.status_code
        return GQLResponse(
            data=data, errors=errors, extensions=extensions, status_code=status_code
        )

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
                    response = service_client.request("GET", url, json=variables)
                case "post":
                    response = service_client.request("POST", url, json=variables)
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


@pytest.fixture(autouse=True)
def passthrough_test_app_calls(request, respx_mock) -> None:
    """
    By default, RESPX asserts that all HTTPX requests are mocked. This is normally
    fine, but in many of our tests, we want to _both_ make real calls to the OS2mo
    FastAPI TestApp while simultaneously mocking the underlying calls to the LoRa app.

    [1] https://lundberg.github.io/respx/api/#configuration
    """
    respx_mock.route(name="mo", url__startswith="http://testserver/").pass_through()
    if "integration_test" in request.keywords:
        respx_mock.route(
            name="lora", url__startswith="http://localhost/lora/"
        ).pass_through()

    yield

    # RESPX asserts that every route - including the pass-through ones - were called.
    # We don't know if the tests will call MO/LoRa, so we have to remove those routes
    # before the check.
    respx_mock.pop("mo")
    if "integration_test" in request.keywords:
        respx_mock.pop("lora")


@pytest.fixture
def mock_organisation(monkeypatch) -> UUID:
    organisation = gen_organisation()

    monkeypatch.setattr(
        Organisation,
        "get_objects_direct",
        AsyncMock(return_value={"results": [[organisation]]}),
    )
    return organisation["id"]


@pytest.fixture
def mock_get_valid_organisations() -> YieldFixture[UUID]:
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


@pytest.fixture(scope="session", name="org_uuids")
def fetch_org_uuids(load_fixture, graphapi_post: GraphAPIPost) -> list[UUID]:
    parent_uuids_query = """
        query FetchOrgUUIDs {
            org_units {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(parent_uuids_query)
    assert response.errors is None
    uuids = list(
        map(UUID, map(itemgetter("uuid"), response.data["org_units"]["objects"]))
    )
    return uuids


@pytest.fixture(scope="session", name="employee_uuids")
def fetch_employee_uuids(load_fixture, graphapi_post: GraphAPIPost) -> list[UUID]:
    parent_uuids_query = """
        query FetchEmployeeUUIDs {
            employees {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(parent_uuids_query)
    assert response.errors is None
    uuids = list(
        map(UUID, map(itemgetter("uuid"), response.data["employees"]["objects"]))
    )
    return uuids


@pytest.fixture(scope="session", name="employee_and_engagement_uuids")
def fetch_employee_and_engagement_uuids(
    load_fixture, graphapi_post: GraphAPIPost
) -> list[tuple[UUID, UUID]]:
    employee_and_engagement_uuids_query = """
        query FetchEmployeeUUIDs {
            employees {
                objects {
                    objects {
                        uuid
                        engagements {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(employee_and_engagement_uuids_query)
    assert response.errors is None
    uuids_and_engagements = [
        {
            "uuid": UUID(obj["uuid"]),
            "engagement_uuids": [
                UUID(engagement["uuid"]) for engagement in obj.get("engagements", [])
            ],
        }
        for employee in response.data["employees"]["objects"]
        for obj in employee["objects"]
        if obj.get("engagements")
    ]

    return uuids_and_engagements


@pytest.fixture(scope="session", name="itsystem_uuids")
def fetch_itsystem_uuids(load_fixture, graphapi_post: GraphAPIPost) -> list[UUID]:
    itsystem_uuids_query = """
        query FetchITSystemUUIDs {
            itsystems {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(itsystem_uuids_query)
    assert response.errors is None
    uuids = list(
        map(UUID, map(itemgetter("uuid"), response.data["itsystems"]["objects"]))
    )
    return uuids


@pytest.fixture(scope="session", name="ituser_uuids")
def fetch_ituser_uuids(load_fixture, graphapi_post: GraphAPIPost) -> list[UUID]:
    ituser_uuids_query = """
        query FetchITSystemUUIDs {
            itusers {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(ituser_uuids_query)
    assert response.errors is None
    uuids = list(
        map(UUID, map(itemgetter("uuid"), response.data["itusers"]["objects"]))
    )
    return uuids


@pytest.fixture(scope="session")
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
    """Fixture yielding a FastAPI test client."""
    return TestClient(fastapi_admin_test_app)


@pytest.fixture(scope="session")
def graphapi_test_no_exc(fastapi_admin_test_app: FastAPI) -> TestClient:
    """Fixture yielding a FastAPI test client.

    This test client does not raise server errors. We use it to check error handling
    in our GraphQL stack.
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


def get_keycloak_token() -> str:
    """Get OIDC token from Keycloak to send to MOs backend.

    Returns:
        Encoded OIDC token from Keycloak
    """
    r = requests.post(
        "http://keycloak:8080/auth/realms/mo/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "mo-frontend",
            "username": "bruce",
            "password": "bruce",
        },
    )
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def token():
    return get_keycloak_token()


@pytest.fixture(scope="session")
def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sp_configuration(monkeypatch, tmp_path) -> None:
    """Configure minimal environment variables to test Serviceplatformen integration."""
    tmp_file = tmp_path / "testfile"
    tmp_file.write_text("This is a certificate")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ENABLE_SP", "True")
    monkeypatch.setenv("SP_CERTIFICATE_PATH", str(tmp_file))
    yield


def create_sessionmaker():
    lora_settings = lora_get_settings()
    return mo_create_sessionmaker(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=_get_dbname(),
    )


@pytest.fixture(scope="session")
async def testing_db_session(testing_db) -> AsyncYieldFixture[AsyncSession]:
    sessionmaker = create_sessionmaker()
    session = sessionmaker()
    yield session
    await session.close()
