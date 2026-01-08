# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import contextvars
import os
import secrets
import traceback
from asyncio import AbstractEventLoopPolicy
from asyncio import DefaultEventLoopPolicy
from asyncio import Task
from collections.abc import AsyncGenerator
from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Generator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial
from operator import itemgetter
from pathlib import Path
from typing import Any
from typing import AsyncContextManager
from typing import Protocol
from typing import TypeVar
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
import requests
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hypothesis import Verbosity
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis.database import InMemoryExampleDatabase
from mora import db
from mora.app import create_app
from mora.auth import middleware as auth_middleware
from mora.auth.keycloak.oidc import Token
from mora.auth.keycloak.oidc import auth
from mora.auth.keycloak.oidc import token_getter
from mora.config import get_settings
from mora.graphapi.gmodels.mo import Validity as GValidity
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.versions.latest.permissions import ALL_PERMISSIONS
from mora.mapping import ADMIN
from mora.service.org import ConfiguredOrganisation
from mora.testing import copy_database
from mora.testing import drop_database
from mora.testing import superuser_connection
from more_itertools import one
from oio_rest.config import Settings as LoraSettings
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.db.alembic_helpers import run_async_upgrade
from oio_rest.organisation import Organisation
from pytest_asyncio import is_async_test
from ramodels.mo import Validity
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette_context import request_cycle_context

from tests.hypothesis_utils import validity_model_strat
from tests.util import MockAioresponses
from tests.util import darmock
from tests.util import load_sample_structures

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


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    # Remove FastRAMQPI fixtures
    # This list should match the list in FastRAMQPIs: pytest_collection_modifyitems
    fastramqpi_integration_test_fixtures = [
        "passthrough_backing_services",
        "fastramqpi_database_setup",
        "fastramqpi_database_isolation",
        "os2mo_database_snapshot_and_restore",
        "amqp_queue_isolation",
        "amqp_event_emitter",
        "graphql_events_quick_fetch",
        "graphql_events_quick_retry",
    ]
    for item in items:
        if item.get_closest_marker("integration_test"):
            for fixture in fastramqpi_integration_test_fixtures:
                if fixture in item.fixturenames:
                    item.fixturenames.remove(fixture)
    # httpx
    for item in items:
        item.add_marker(pytest.mark.respx(using="httpx"))
    # pytest-asyncio
    # https://pytest-asyncio.readthedocs.io/en/latest/how-to-guides/run_session_tests_in_same_loop.html
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker)


@pytest.fixture(autouse=True)
def set_testing_environment_variables() -> None:
    os.environ["TESTING"] = "True"
    os.environ["PYTEST_RUNNING"] = "True"


st.register_type_strategy(Validity, validity_model_strat())
st.register_type_strategy(GValidity, validity_model_strat())


@pytest.fixture(autouse=True)
def clear_configured_organisation():
    ConfiguredOrganisation.clear()


@pytest.fixture(autouse=True)
def clear_actor_cache():
    auth_middleware._actor_cache.clear()


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


BRUCE_UUID = UUID("99e7b256-7dfa-4ee8-95c6-e3abe82e236a")


async def fake_auth() -> Token:
    return Token(
        azp="vue",
        email="bruce@kung.fu",
        preferred_username="bruce",
        realm_access={"roles": {"service_api"}},
        uuid=str(BRUCE_UUID),
    )


async def serviceapiless_auth() -> Token:
    auth = await fake_auth()
    auth.realm_access.roles = set()
    return auth


async def admin_auth() -> Token:
    auth = await fake_auth()
    auth.realm_access.roles = {"admin", "owner", "service_api"}.union(ALL_PERMISSIONS)
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


SetAuth = Callable[[str | None, UUID | str | None, str], None]


@pytest.fixture
def set_auth(
    fastapi_admin_test_app: FastAPI,
) -> SetAuth:
    """Set authentication token used by GraphAPIPost."""

    def _set_auth(
        role: str | None = None,
        user_uuid: UUID | str | None = None,
        preferred_username: str = "bruce",
    ) -> None:
        token_data = {
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
            "preferred_username": preferred_username,
            "scope": "email profile",
            "session_state": "d94f8dc3-d930-49b3-a9dd-9cdc1893b86a",
            "sub": "c420894f-36ba-4cd5-b4f8-1b24bd8c53db",
            "typ": "Bearer",
            "uuid": str(user_uuid) if user_uuid is not None else None,
        }
        if role is not None:
            if role == ADMIN:
                roles = ALL_PERMISSIONS
            else:
                roles = {role}
            token_data["realm_access"] = {"roles": roles}
        token = Token.parse_obj(token_data)

        def _auth():
            return token

        def _token_getter():
            async def _get():
                return token

            return _get

        fastapi_admin_test_app.dependency_overrides[auth] = _auth
        fastapi_admin_test_app.dependency_overrides[token_getter] = _token_getter

    return _set_auth


class SessionmakerMaker:
    def __init__(self, sessionmaker) -> None:
        self.sessionmaker = sessionmaker
        self.database_name = None

    def get_sessionmaker(self, _):
        return self.sessionmaker

    def get_database_name(self):
        if self.database_name is None:
            pytest.fail(
                "Improperly-configured test: you are probably trying to access the database without requesting a database fixture"
            )
        return self.database_name


class FakeDatabaseSession:
    def __getattr__(self, attr):
        if attr == "begin":

            @asynccontextmanager
            async def session_begin():
                yield

            return session_begin
        elif attr == "rollback":
            # rollback allowed so we can test GraphQL fails, e.g. schema
            # validation functions.
            async def noop(): ...

            return noop
        elif attr == "under_testing_with_fake_db":
            return True
        else:
            pytest.fail("This test is not connected to a database")


@pytest.fixture
def sessionmakermaker() -> SessionmakerMaker:
    @asynccontextmanager
    async def sessionmaker():
        yield FakeDatabaseSession()

    return SessionmakerMaker(sessionmaker=sessionmaker)


@pytest.fixture(autouse=True)
async def mocked_context() -> YieldFixture[None]:
    """
    Testing code that relies on context vars without a full test client / app.
    https://starlette-context.readthedocs.io/en/latest/testing.html
    """
    # NOTE: This fixture MUST be async to ensure the context is propagated correctly
    # to the tests.
    assert asyncio.get_running_loop()
    data = {db._DB_SESSION_CONTEXT_KEY: FakeDatabaseSession()}
    with request_cycle_context(data):
        yield


@pytest.fixture
def fastapi_test_app(monkeypatch, sessionmakermaker) -> FastAPI:
    app = create_app()
    monkeypatch.setattr(db, "_get_sessionmaker", sessionmakermaker.get_sessionmaker)
    app.dependency_overrides[auth] = fake_auth
    app.dependency_overrides[token_getter] = fake_token_getter
    return app


@pytest.fixture
def fastapi_admin_test_app(monkeypatch, sessionmakermaker) -> FastAPI:
    app = create_app()
    monkeypatch.setattr(db, "_get_sessionmaker", sessionmakermaker.get_sessionmaker)
    app.dependency_overrides[auth] = admin_auth
    app.dependency_overrides[token_getter] = admin_token_getter
    return app


@pytest.fixture(scope="session")
def latest_graphql_url() -> str:
    return f"/graphql/v{LATEST_VERSION.value}"


@pytest.fixture
def raw_client(monkeypatch, sessionmakermaker) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    app = create_app()
    monkeypatch.setattr(db, "_get_sessionmaker", sessionmakermaker.get_sessionmaker)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def service_client(fastapi_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    with TestClient(fastapi_test_app) as client:
        yield client


@pytest.fixture
def admin_client(fastapi_admin_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    with TestClient(fastapi_admin_test_app) as client:
        yield client


@pytest.fixture
def service_client_not_raising(fastapi_test_app: FastAPI) -> YieldFixture[TestClient]:
    """Fixture yielding a FastAPI test client."""
    with TestClient(fastapi_test_app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture(scope="session")
def lora_settings() -> LoraSettings:
    return lora_get_settings()


@pytest.fixture(scope="session")
async def superuser(lora_settings: LoraSettings) -> AsyncYieldFixture[AsyncConnection]:
    async with superuser_connection(lora_settings) as connection:
        yield connection


@asynccontextmanager
async def _database_copy(superuser: AsyncConnection, source: str) -> AsyncIterator[str]:
    """Copy database and return the copy's name."""
    # Generate random destination name to support reentrancy for the same source
    destination = f"{source}_copy_{secrets.token_hex(4)}"
    await copy_database(superuser, source, destination)
    yield destination
    await drop_database(superuser, destination)


def _create_sessionmaker(lora_settings: LoraSettings, database_name: str):
    return db.create_sessionmaker(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=database_name,
    )


@asynccontextmanager
async def _use_session(
    lora_settings: LoraSettings, database_name: str
) -> AsyncIterator[tuple[async_sessionmaker, db.AsyncSession]]:
    """Patch mora to connect to the provided `database_name`."""
    sessionmaker = _create_sessionmaker(lora_settings, database_name)
    async with sessionmaker() as session, session.begin():
        data = {db._DB_SESSION_CONTEXT_KEY: session}
        with request_cycle_context(data):
            yield sessionmaker, session


AnotherTransaction = Callable[
    [],
    AsyncContextManager[tuple[async_sessionmaker, db.AsyncSession]],
]


@pytest.fixture
async def another_transaction(
    lora_settings: LoraSettings, sessionmakermaker: SessionmakerMaker
) -> AnotherTransaction:
    """This fixture can be used as an async context manager to create a
    separate database transaction.

    Remember that web requests - such as those made with the graphapi_post and
    service_client fixtures - already run in their own transaction.

    This fixture should be used when calls are made directly, e.g. with the
    lora connector or when loading data.
    """

    def inner() -> AsyncContextManager[tuple[async_sessionmaker, db.AsyncSession]]:
        return _use_session(lora_settings, sessionmakermaker.get_database_name())

    return inner


@pytest.fixture(scope="session")
async def empty_database_template(
    superuser: AsyncConnection, lora_settings: LoraSettings
) -> AsyncYieldFixture[str]:
    async with _database_copy(superuser, "template1") as database_name:
        # Apply alembic migrations
        async with _use_session(lora_settings, database_name) as (_, session):
            connection = await session.connection()
            await run_async_upgrade(connection.engine)
        yield database_name


@pytest.fixture(scope="session")
async def fixture_database_template(
    superuser: AsyncConnection,
    lora_settings: LoraSettings,
    empty_database_template: str,
) -> AsyncYieldFixture[str]:
    async with _database_copy(superuser, empty_database_template) as database_name:
        # Load fixture data
        async with _use_session(lora_settings, database_name):
            await load_sample_structures()
        yield database_name


@pytest.fixture
async def empty_db(
    superuser: AsyncConnection,
    lora_settings: LoraSettings,
    empty_database_template: str,
    sessionmakermaker: SessionmakerMaker,
) -> AsyncYieldFixture[async_sessionmaker]:
    async with (
        _database_copy(superuser, empty_database_template) as database_name,
        _use_session(lora_settings, database_name) as (sessionmaker, session),
    ):
        sessionmakermaker.sessionmaker = sessionmaker
        sessionmakermaker.database_name = database_name
        yield session


@pytest.fixture
async def fixture_db(
    superuser: AsyncConnection,
    lora_settings: LoraSettings,
    fixture_database_template: str,
    sessionmakermaker: SessionmakerMaker,
) -> AsyncYieldFixture[async_sessionmaker]:
    async with (
        _database_copy(superuser, fixture_database_template) as database_name,
        _use_session(lora_settings, database_name) as (sessionmaker, session),
    ):
        sessionmakermaker.sessionmaker = sessionmaker
        sessionmakermaker.database_name = database_name
        yield session


@pytest.fixture(scope="session", autouse=True)
def event_loop_policy() -> AbstractEventLoopPolicy:
    """Custom implementation of pytest-asyncio's event_loop_policy fixture[1].

    This fixture is used by pytest-asyncio to run test's setup/run/teardown. It
    is needed to share contextvars between these stages; without it,
    contextvars from async coroutine fixtures are not passed correctly to the
    individual tests. See the issue[2] with solution implementation[3].

    The fixture name shadows the default fixture from pytest-asyncio, and thus
    overrides it. Note that the links below reference overwriting the event_loop
    fixture instead of the event_loop_policy -- this has been deprecated.

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
            if package_name != "asyncio":
                if package_name == "pytest_asyncio":
                    # This function was called from pytest_asyncio, use shared context
                    break
                else:
                    # This function was called from somewhere else, create context copy
                    context = None
                break
        return Task(coro, loop=loop, context=context)

    context = contextvars.copy_context()

    class CustomEventLoopPolicy(DefaultEventLoopPolicy):
        def new_event_loop(self):
            loop = super().new_event_loop()
            loop.set_task_factory(partial(task_factory, context=context))
            return loop

    return CustomEventLoopPolicy()


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
    ) -> GQLResponse: ...


@pytest.fixture
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


@pytest.fixture
def serviceapi_post(service_client: TestClient):
    def _post(
        url: str,
        variables: dict[str, Any] | None = None,
        method: str = "get",
    ) -> ServiceAPIResponse:
        try:
            match method.lower():
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


@pytest.fixture
@pytest.mark.usefixtures("fixture_db")
def org_uuids(graphapi_post: GraphAPIPost) -> list[UUID]:
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


@pytest.fixture
@pytest.mark.usefixtures("fixture_db")
def employee_uuids(graphapi_post: GraphAPIPost) -> list[UUID]:
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


@pytest.fixture
@pytest.mark.usefixtures("fixture_db")
def employee_and_engagement_uuids(
    graphapi_post: GraphAPIPost,
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


@pytest.fixture
@pytest.mark.usefixtures("fixture_db")
def trade_union_uuids(graphapi_post: GraphAPIPost) -> list[UUID]:
    # Fixture that creates the facet "medarbejderorganisation" and a class under that facet called "AC (Akademikerne)"
    facet_mutate_query = """
        mutation CreateFacet($input: FacetCreateInput!) {
            facet_create(input: $input) {
                uuid
            }
        }
    """

    facet_response = graphapi_post(
        facet_mutate_query,
        {
            "input": {
                "user_key": "medarbejderorganisation",
                "validity": {"from": "2017-01-01T00:00:00+01:00"},
            }
        },
    )
    assert facet_response.errors is None
    assert facet_response.data is not None

    class_mutate_query = """
        mutation CreateClass($input: ClassCreateInput!) {
            class_create(input: $input) {
                uuid
            }
        }
    """
    class_response = graphapi_post(
        class_mutate_query,
        {
            "input": {
                "name": "AC (Akademikerne)",
                "user_key": "ac",
                "facet_uuid": facet_response.data["facet_create"]["uuid"],
                "validity": {"from": "2017-01-02T00:00:00+01:00"},
            }
        },
    )
    assert class_response.errors is None
    assert class_response.data is not None

    classes_query = """
        query FetchDynamicClasses {
            classes(filter: {facet: {user_keys: "medarbejderorganisation"}}) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(classes_query)
    assert response.errors is None
    assert response.data is not None
    return [UUID(obj["uuid"]) for obj in response.data["classes"]["objects"]]


@pytest.fixture
@pytest.mark.usefixtures("fixture_db")
def itsystem_uuids(graphapi_post: GraphAPIPost) -> list[UUID]:
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


@pytest.fixture
@pytest.mark.usefixtures("fixture_db")
def ituser_uuids(graphapi_post: GraphAPIPost) -> list[UUID]:
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


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {get_keycloak_token()}"}


@pytest.fixture
def sp_configuration(monkeypatch, tmp_path) -> None:
    """Configure minimal environment variables to test Serviceplatformen integration."""
    tmp_file = tmp_path / "testfile"
    tmp_file.write_text("This is a certificate")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ENABLE_SP", "True")
    monkeypatch.setenv("SP_CERTIFICATE_PATH", str(tmp_file))
    yield


@pytest.fixture
def create_org(graphapi_post: GraphAPIPost) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        org_create_mutation = """
            mutation CreateOrganisation($input: OrganisationCreate!) {
                org_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(org_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        org_uuid = response.data["org_create"]["uuid"]
        return org_uuid

    return inner


@pytest.fixture
def root_org(create_org: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_org({"municipality_code": None})


@pytest.fixture
def create_org_unit(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[str, UUID | None], UUID]:
    def inner(user_key: str, parent: UUID | None = None) -> UUID:
        mutate_query = """
            mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "name": user_key,
                    "user_key": user_key,
                    "parent": str(parent) if parent else None,
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                    "org_unit_type": str(uuid4()),
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_create"]["uuid"])

    return inner


@pytest.fixture
def create_person(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any] | None], UUID]:
    def inner(input: dict[str, Any] | None = None) -> UUID:
        input = input or {
            "given_name": str(uuid4()),
            "surname": str(uuid4()),
        }

        mutate_query = """
            mutation CreatePerson($input: EmployeeCreateInput!) {
                employee_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["employee_create"]["uuid"])

    return inner


@pytest.fixture
def update_person(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdatePerson($input: EmployeeUpdateInput!) {
                employee_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["employee_update"]["uuid"])

    return inner


@pytest.fixture
def create_manager(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[UUID, UUID | None], UUID]:
    def inner(org_unit: UUID, person: UUID | None = None) -> UUID:
        mutate_query = """
            mutation CreateManager($input: ManagerCreateInput!) {
                manager_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "manager_level": str(uuid4()),
                    "manager_type": str(uuid4()),
                    "responsibility": [],
                    "org_unit": str(org_unit),
                    "person": str(person) if person else None,
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_create"]["uuid"])

    return inner


@pytest.fixture
def update_manager(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[UUID, UUID | None], UUID]:
    def inner(manager_uuid: UUID, person: UUID | None = None) -> UUID:
        mutate_query = """
            mutation UpdateManager($input: ManagerUpdateInput!) {
                manager_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "uuid": str(manager_uuid),
                    "person": str(person) if person else None,
                    "validity": {"from": "1980-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["manager_update"]["uuid"])

    return inner


@pytest.fixture
def create_facet(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        facet_create_mutation = """
            mutation CreateFacet($input: FacetCreateInput!) {
                facet_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(facet_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return response.data["facet_create"]["uuid"]

    return inner


@pytest.fixture
def update_facet(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateFacet($input: FacetUpdateInput!) {
                facet_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["facet_update"]["uuid"])

    return inner


@pytest.fixture
def org_unit_type_facet(create_facet: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_facet(
        {
            "user_key": "org_unit_type",
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def role_facet(create_facet: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_facet(
        {
            "user_key": "role",
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def create_itsystem(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        itsystem_create_mutation = """
            mutation CreateITSystem($input: ITSystemCreateInput!) {
                itsystem_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(itsystem_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        itsystem_uuid = UUID(response.data["itsystem_create"]["uuid"])
        return itsystem_uuid

    return inner


@pytest.fixture
def update_itsystem(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateITSystem($input: ITSystemUpdateInput!) {
                itsystem_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["itsystem_update"]["uuid"])

    return inner


@pytest.fixture
def create_class(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        class_create_mutation = """
            mutation CreateRole($input: ClassCreateInput!) {
                class_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(class_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        class_uuid = UUID(response.data["class_create"]["uuid"])
        return class_uuid

    return inner


@pytest.fixture
def update_class(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateClass($input: ClassUpdateInput!) {
                class_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["class_update"]["uuid"])

    return inner


@pytest.fixture
def create_ituser(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        ituser_create_mutation = """
            mutation ITUserCreate($input: ITUserCreateInput!) {
                ituser_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(ituser_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["ituser_create"]["uuid"])

    return inner


@pytest.fixture
def create_rolebinding(
    graphapi_post: GraphAPIPost, root_org: UUID
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        rolebinding_create_mutation = """
            mutation RoleBindingCreate($input: RoleBindingCreateInput!) {
                rolebinding_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(rolebinding_create_mutation, {"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["rolebinding_create"]["uuid"])

    return inner


@pytest.fixture
def read_rolebinding_uuids(
    graphapi_post: GraphAPIPost,
) -> Callable[[dict[str, Any]], set[UUID]]:
    def inner(filter: dict[str, Any]) -> set[UUID]:
        rolebinding_uuid_query = """
            query ReadRoleBindings($filter: RoleBindingFilter) {
                rolebindings(filter: $filter) {
                    objects {
                        uuid
                    }
                }
            }
        """
        response = graphapi_post(rolebinding_uuid_query, {"filter": filter})
        assert response.errors is None
        assert response.data
        return {UUID(obj["uuid"]) for obj in response.data["rolebindings"]["objects"]}

    return inner


@pytest.fixture
def create_address(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation CreateAddress($input: AddressCreateInput!) {
                address_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["address_create"]["uuid"])

    return inner


@pytest.fixture
def update_address(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> Callable[[dict[str, Any]], UUID]:
    def inner(input: dict[str, Any]) -> UUID:
        mutate_query = """
            mutation UpdateAddress($input: AddressUpdateInput!) {
                address_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(query=mutate_query, variables={"input": input})
        assert response.errors is None
        assert response.data
        return UUID(response.data["address_update"]["uuid"])

    return inner
