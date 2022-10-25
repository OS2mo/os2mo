# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
from typing import Any
from typing import Callable
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mo_ldap_import_export.main import create_app


@pytest.fixture
def fastapi_app_builder(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Callable[..., FastAPI], None, None]:
    """Fixture for the FastAPI app builder."""

    monkeypatch.setenv("CLIENT_ID", "dipex")
    monkeypatch.setenv("client_secret", "603f1c82-d012-4d04-9382-dbe659c533fb")
    monkeypatch.setenv("AD_CONTROLLERS", '[{"host": "100.110.188.107"}]')
    monkeypatch.setenv("AD_DOMAIN", "AD")
    monkeypatch.setenv("AD_USER", "nj")
    monkeypatch.setenv("AD_PASSWORD", "Torsdag123")
    monkeypatch.setenv("AD_SEARCH_BASE", "DC=ad,DC=addev")

    def builder(*args: Any, **kwargs: Any) -> FastAPI:

        return create_app(*args, **kwargs)

    yield builder


@pytest.fixture
def test_client_builder(
    fastapi_app_builder: Callable[..., FastAPI]
) -> Generator[Callable[..., TestClient], None, None]:
    """Fixture for the FastAPI test client builder."""

    def builder(*args: Any, **kwargs: Any) -> TestClient:
        return TestClient(fastapi_app_builder(*args, **kwargs))

    yield builder


async def test_trigger_all_endpoint(
    test_client_builder: Callable[..., TestClient],
) -> None:
    """Test the trigger all endpoint on our app."""
    # test_client = test_client_builder()

    # response = test_client.get("/all")
    # assert response.status_code == 202
    # print("=" * 50)
    # print("This is the output of the request:")
    # for p in response.json()[-10:]:
    #     print(p)
    # print("=" * 50)
    pass
