#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import os
from dataclasses import dataclass
from typing import Any
from typing import Optional

import pytest
from aioresponses import aioresponses as aioresponses_
from fastapi.testclient import TestClient
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis import Verbosity
from hypothesis.database import InMemoryExampleDatabase
from starlette_context import _request_scope_context_storage
from starlette_context.ctx import _Context

from .legacy.cases import fake_auth
from .legacy.hypothesis_utils import validity_model_strat
from .legacy.util import _mox_testing_api
from .legacy.util import load_sample_structures
from mora.api.v1.models import Validity
from mora.http import clients
from mora.app import create_app
from mora.auth.keycloak.oidc import auth

# --------------------------------------------------------------------------------------
# Configs + fixtures
# --------------------------------------------------------------------------------------
h_db = InMemoryExampleDatabase()
h_settings.register_profile("ci", max_examples=100, deadline=None, database=h_db)
h_settings.register_profile("dev", max_examples=10, deadline=None, database=h_db)
h_settings.register_profile(
    "debug", max_examples=10, verbosity=Verbosity.verbose, database=h_db
)
h_settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


def pytest_runtest_setup(item):
    os.environ["PYTEST_RUNNING"] = "True"


def pytest_configure(config):
    config.addinivalue_line("markers", "serial: mark test to run serially")


st.register_type_strategy(Validity, validity_model_strat())


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


@pytest.fixture(autouse=True)
async def init_clients():
    await clients.init_clients()


@pytest.fixture
def aioresponses():
    """Pytest fixture for aioresponses."""
    with aioresponses_() as aior:
        yield aior


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
def service_test_client():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(test_app()) as client:
        yield client


@pytest.fixture()
def service_test_client_not_raising():
    """Fixture yielding a FastAPI test client.

    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    with TestClient(test_app(), raise_server_exceptions=False) as client:
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
