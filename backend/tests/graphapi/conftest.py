#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Pytest configurations for GraphAPI tests.

This file specifies different pytest fixtures and settings shared throughout the
GraphAPI test suite. Some are autoused for each test invocation, while others are made
available for use as needed.
"""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import json
from pathlib import Path
from typing import List
from typing import Optional
from uuid import UUID

import pytest
from aioresponses import aioresponses as aioresp
from aioresponses.core import URL
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mora import util as mora_util
from mora.graphapi.dataloaders import MOModel
from mora.graphapi.main import get_loaders
from mora.graphapi.main import get_schema
from mora.graphapi.main import setup_graphql
from mora.lora import LoraObjectType
from tests.util import patch_is_graphql


# --------------------------------------------------------------------------------------
# Shared fixtures
# --------------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_context(monkeypatch):
    """Patch the context.

    This fixture is autoused and is primarily necessary when our LoRa
    readers are not mocked.
    """
    monkeypatch.setattr(mora_util, "get_args_flag", lambda *args: False)
    with patch_is_graphql(True):
        yield


# --------------------------------------------------------------------------------------
# Dataloader patch fixture
# --------------------------------------------------------------------------------------


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


# --------------------------------------------------------------------------------------
# LoRa mock fixtures
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def lora_data():
    """Fixture to load LoRa mock data from disk.

    This fixture is session scoped because we do not need teardowns between tests,
    and session scoping ensures we only call this once per test session.
    """
    data_path = Path(__file__).parent / "_data"
    data = dict()
    for lora_obj in LoraObjectType:
        fixture_file = data_path / f"{lora_obj.name}.json"
        data[lora_obj.name] = json.loads(fixture_file.read_text())
    yield data


@pytest.fixture(scope="session")
def lora_ids(lora_data):
    """Fixture to get LoRa UUIDs for tests.

    This fixture is session scoped because we do not need teardowns between tests,
    and session scoping ensures we only call this once per test session.
    """
    ids = dict()
    for name, value in lora_data.items():
        ids[name] = {UUID(result["id"]) for result in value["results"][0]}
    yield ids


@pytest.fixture(scope="session")
def lora_mock(lora_data):
    """Fixture to mock responses from LoRa.

    This fixture mocks all LoRa endpoints as requested by MO (cf. LoraObjectType).
    It is session scoped because we do not need teardowns between tests,
    and session scoping ensures we only call this once per test session.
    """
    with aioresp() as mock:
        for lora_obj in LoraObjectType:
            lora_url = f"http://mox/{lora_obj.value}"
            payload = lora_data[lora_obj.name]
            mock.get(
                URL(lora_url),
                payload=payload,
                repeat=True,
            )
        yield mock


# --------------------------------------------------------------------------------------
# FastAPI GraphAPI test client
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="class")
def graphapi_test():
    """Fixture yielding a FastAPI test client.

    Only the GraphAPI endpoint is available.
    This fixture is class scoped to ensure safe teardowns between test classes.
    """
    app = FastAPI()
    gql_router = setup_graphql()
    app.include_router(gql_router, prefix="/graphql")
    yield TestClient(app)


# --------------------------------------------------------------------------------------
# GraphAPI schema fixture
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="class")
def execute():
    """Fixture to execute queries, optionally with values, against our GraphQL schema.

    If dataloaders are mocked, this should always be called within the same context,
    but *after* the actual mock. Otherwise, the loaders context value will not
    pick up the mock correctly.
    """

    async def _execute(query: str, values: Optional[dict] = None):
        schema = get_schema()
        loaders = await get_loaders()
        result = await schema.execute(
            query, variable_values=values, context_value=loaders
        )
        return result

    yield _execute
