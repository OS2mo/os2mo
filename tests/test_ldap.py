#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:03:16 2022

@author: nick
"""
import asyncio
import os
from collections.abc import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from ldap3 import Connection
from ldap3 import MOCK_SYNC
from ldap3 import Server

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server
from mo_ldap_import_export.ldap import get_client_strategy
from mo_ldap_import_export.ldap import ldap_healthcheck


@pytest.fixture
def ldap_connection() -> Iterator[MagicMock]:
    """Fixture to construct a mock ldap_connection.

    Yields:
        A mock for ldap_connection.
    """
    yield MagicMock()


@pytest.fixture
def settings_overrides() -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings.

    Yields:
        Minimal set of overrides.
    """
    overrides = {
        "LDAP_CONTROLLERS": '[{"host": "111.111.111.111"}]',
        "CLIENT_ID": "foo",
        "CLIENT_SECRET": "bar",
        "LDAP_DOMAIN": "LDAP",
        "LDAP_USER": "foo",
        "LDAP_PASSWORD": "foo",
        "LDAP_SEARCH_BASE": "DC=ad,DC=addev",
        "LDAP_ORGANIZATIONAL_UNIT": "OU=Magenta",
    }
    yield overrides


@pytest.fixture
def load_settings_overrides(
    settings_overrides: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> Iterator[dict[str, str]]:
    """Fixture to set happy-path settings overrides as environmental variables.

    Note:
        Only loads environmental variables, if variables are not already set.

    Args:
        settings_overrides: The list of settings to load in.
        monkeypatch: Pytest MonkeyPatch instance to set environmental variables.

    Yields:
        Minimal set of overrides.
    """
    for key, value in settings_overrides.items():
        if os.environ.get(key) is not None:
            continue
        monkeypatch.setenv(key, value)
    yield settings_overrides


def test_construct_server(load_settings_overrides: dict[str, str]) -> None:
    settings = Settings()

    server = construct_server(settings.ldap_controllers[0])
    assert isinstance(server, Server)


def test_configure_ldap_connection(load_settings_overrides: dict[str, str]) -> None:

    settings = Settings()

    with patch(
        "mo_ldap_import_export.ldap.get_client_strategy", return_value=MOCK_SYNC
    ):
        connection = configure_ldap_connection(settings)
        assert isinstance(connection, Connection)


def test_get_client_strategy() -> None:
    strategy = get_client_strategy()
    assert strategy == "RESTARTABLE"


async def test_ldap_healthcheck(ldap_connection: MagicMock) -> None:

    for bound in [True, False]:
        ldap_connection.bound = bound
        context = {"user_context": {"ldap_connection": ldap_connection}}

        check = await asyncio.gather(ldap_healthcheck(context))

        assert check[0] == bound
