#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import asyncio
import datetime
import os
import re
from dataclasses import dataclass
from datetime import date
from datetime import timedelta
from functools import lru_cache
from functools import partial
from re import Pattern
from typing import Any
from typing import Callable
from typing import Generator
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis import Verbosity
from hypothesis.database import InMemoryExampleDatabase
from pydantic import ValidationError
from respx.mocks import HTTPCoreMocker
from starlette_context import _request_scope_context_storage
from starlette_context.ctx import _Context

from mora import lora
from mora.app import create_app
from mora.auth.keycloak.oidc import auth
from mora.config import get_settings
from mora.service.org import ConfiguredOrganisation
from ramodels.mo import Validity
from tests.hypothesis_utils import validity_model_strat
from tests.util import _mox_testing_api
from tests.util import load_sample_structures

# --------------------------------------------------------------------------------------
# Configs + fixtures
# --------------------------------------------------------------------------------------
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


def pytest_runtest_setup(item):
    os.environ["PYTEST_RUNNING"] = "True"


def pytest_configure(config):
    config.addinivalue_line("markers", "serial: mark test to run serially")
    config.addinivalue_line("markers", "equivalence: mark test as equivalence test")


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


@pytest.fixture
async def sample_structures_no_reset(testing_db):
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=False)
    yield


@pytest.fixture
async def sample_structures(testing_db):
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=False)
    yield
    _mox_testing_api("db-reset")


@pytest.fixture
async def sample_structures_minimal(testing_db):
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=True)
    yield
    _mox_testing_api("db-reset")


@pytest.fixture()
def service_test_client(fastapi_test_app):
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_test_app) as client:
        yield client


@pytest.fixture()
def service_test_client_not_raising(fastapi_test_app):
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(fastapi_test_app, raise_server_exceptions=False) as client:
        yield client


@dataclass
class GQLResponse:
    data: Optional[dict]
    errors: Optional[list[dict]]
    status_code: int


@pytest.fixture(scope="class")
def graphapi_post(graphapi_test: TestClient):
    def _post(query: str, variables: Optional[dict[str, Any]] = None) -> GQLResponse:
        with graphapi_test as client:
            response = client.post(
                "/graphql", json={"query": query, "variables": variables}
            )
        data, errors = response.json().get("data"), response.json().get("errors")
        status_code = response.status_code
        return GQLResponse(data=data, errors=errors, status_code=status_code)

    yield _post


def gen_organisation(
    uuid: Optional[UUID] = None,
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


unexpected_value_error = partial(
    pytest.raises, ValidationError, match="unexpected value;"
)


@st.composite
def tz_dt_strat(draw):
    dts = st.datetimes(
        min_value=datetime(1930, 1, 1),
        timezones=st.timezones(),
        allow_imaginary=False,
    )
    return draw(dts)


date_strat = partial(st.dates, min_value=date(1930, 1, 1))


@st.composite
def dt_minmax(draw):
    dt_shared = st.shared(date_strat(), key="dtminmax")
    return draw(dt_shared)


@st.composite
def from_date_strat(draw):
    max_date = draw(dt_minmax())
    dates = date_strat(max_value=max_date).map(lambda date: date.isoformat())
    return draw(dates)


@st.composite
def to_date_strat(draw):
    min_date = draw(dt_minmax()) + timedelta(days=1)
    dates = st.dates(min_value=min_date).map(lambda date: date.isoformat())
    return draw(dates)


@st.composite
def not_from_regex(draw, str_pat: str):
    @lru_cache
    def cached_regex(str_pat: str) -> Pattern:
        return re.compile(str_pat)

    regex = cached_regex(str_pat)
    not_match = st.text().filter(lambda s: regex.match(s) is None)
    return draw(not_match)


@st.composite
def validity_strat(draw):
    required = {"from_date": from_date_strat()}
    optional = {"to_date": st.none() | to_date_strat()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def validity_model_strat(draw) -> Validity:
    st_dict = draw(validity_strat())
    return Validity(**st_dict)


st.register_type_strategy(Validity, validity_model_strat())
