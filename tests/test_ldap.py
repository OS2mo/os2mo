#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:03:16 2022

@author: nick
"""
import asyncio
import os
from collections.abc import Iterator
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fastramqpi.context import Context
from ldap3 import Connection
from ldap3 import MOCK_SYNC
from ldap3 import Server
from more_itertools import collapse

from .test_dataloaders import mock_ldap_response
from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server
from mo_ldap_import_export.ldap import get_client_strategy
from mo_ldap_import_export.ldap import get_ldap_attributes
from mo_ldap_import_export.ldap import is_dn
from mo_ldap_import_export.ldap import ldap_healthcheck
from mo_ldap_import_export.ldap import make_ldap_object
from mo_ldap_import_export.ldap import paged_search
from mo_ldap_import_export.ldap import single_object_search
from mo_ldap_import_export.ldap_classes import LdapObject


@pytest.fixture()
def ldap_attributes() -> dict:
    return {"department": None, "name": "John", "employeeID": "0101011234"}


@pytest.fixture
def cpr_field() -> str:
    return "employeeID"


@pytest.fixture
def gql_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def model_client() -> Iterator[AsyncMock]:
    yield AsyncMock()


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLIENT_ID", "foo")
    monkeypatch.setenv("client_secret", "bar")
    monkeypatch.setenv("LDAP_CONTROLLERS", '[{"host": "0.0.0.0"}]')
    monkeypatch.setenv("LDAP_DOMAIN", "LDAP")
    monkeypatch.setenv("LDAP_USER", "foo")
    monkeypatch.setenv("LDAP_PASSWORD", "bar")
    monkeypatch.setenv("LDAP_SEARCH_BASE", "DC=ad,DC=addev")
    monkeypatch.setenv("LDAP_ORGANIZATIONAL_UNIT", "OU=Magenta")

    return Settings()


@pytest.fixture
def ldap_connection() -> Iterator[MagicMock]:
    """Fixture to construct a mock ldap_connection.

    Yields:
        A mock for ldap_connection.
    """
    yield MagicMock()


@pytest.fixture
def context(
    ldap_connection: MagicMock,
    gql_client: AsyncMock,
    model_client: AsyncMock,
    settings: Settings,
    cpr_field: str,
) -> Context:

    return {
        "user_context": {
            "settings": settings,
            "ldap_connection": ldap_connection,
            "gql_client": gql_client,
            "model_client": model_client,
            "cpr_field": cpr_field,
        },
    }


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


async def test_is_dn():
    dn = "CN=Harry Styles,OU=Band,DC=Stage"
    assert is_dn(dn) is True
    not_a_dn = "foo"
    assert is_dn(not_a_dn) is False


async def test_make_generic_ldap_object(cpr_field: str, context: Context):

    response: dict[str, Any] = {}
    response["dn"] = "CN=Harry Styles,OU=Band,DC=Stage"
    response["attributes"] = {
        "Name": "Harry",
        "Occupation": "Douchebag",
        "manager": "CN=Jonie Mitchell,OU=Band,DC=Stage",
    }

    ldap_object = make_ldap_object(response, context, nest=False)

    expected_ldap_object = LdapObject(**response["attributes"], dn=response["dn"])

    assert ldap_object == expected_ldap_object


async def test_make_nested_ldap_object(cpr_field: str, context: Context):

    # Here we expect the manager's entry to be another ldap object instead of a string
    # As well as the band members
    attributes_without_nests = {
        "Name": "Harry",
        "Occupation": "Douchebag",
    }

    response: dict[str, Any] = {}
    response["dn"] = "CN=Harry Styles,OU=Band,DC=Stage"
    response["attributes"] = attributes_without_nests.copy()
    response["attributes"]["manager"] = "CN=Jonie Mitchell,OU=Band,DC=Stage"
    response["attributes"]["band_members"] = [
        "CN=George Harrisson,OU=Band,DC=Stage",
        "CN=Ringo Starr,OU=Band,DC=Stage",
    ]
    response["attributes"][cpr_field] = "0101011234"

    # But we do not expect the manager and band members friends or buddies to be
    # ldap objects
    nested_response: dict[str, Any] = {}
    nested_response["dn"] = "CN=Person with affiliation to Harry, OU=Band, DC=Stage"
    nested_response["attributes"] = {
        "Name": "Anonymous",
        "Occupation": "Slave",
        "best_friend": "CN=God,OU=Band,DC=Stage",
        "buddies": [
            "CN=Satan,OU=Band,DC=Stage",
            "CN=Vladimir,OU=Band,DC=Stage",
        ],
    }

    with patch(
        "mo_ldap_import_export.ldap.single_object_search",
        return_value=nested_response,
    ):
        ldap_object = make_ldap_object(response, context, nest=True)

    # harry is an Employee because he has a cpr no.
    assert type(ldap_object) == LdapObject

    # The manager is generic because she does not have a cpr no.
    assert type(ldap_object.manager) == LdapObject  # type: ignore

    # The manager's buddies are dns because we only nest 1 level
    assert is_dn(ldap_object.manager.best_friend) is True  # type: ignore
    assert is_dn(ldap_object.manager.buddies[0]) is True  # type: ignore
    assert is_dn(ldap_object.manager.buddies[1]) is True  # type: ignore

    # The band members are generic because they do not have a cpr no.
    assert type(ldap_object.band_members) == list  # type: ignore
    assert type(ldap_object.band_members[0]) == LdapObject  # type: ignore
    assert type(ldap_object.band_members[1]) == LdapObject  # type: ignore


async def test_get_ldap_attributes():
    ldap_connection = MagicMock()

    # Simulate 3 levels
    levels = ["bottom", "middle", "top", None]
    expected_attributes = [["mama", "papa"], ["brother", "sister"], ["wife"], None]

    expected_output = list(collapse(expected_attributes[:3]))

    # Format object_classes dict
    object_classes = {}
    for i in range(len(levels) - 1):
        schema = MagicMock()

        schema.may_contain = expected_attributes[i]
        schema.superior = levels[i + 1]
        object_classes[levels[i]] = schema

    # Add to mock
    ldap_connection.server.schema.object_classes = object_classes

    # test the function
    output = get_ldap_attributes(ldap_connection, str(levels[0]))
    assert output == expected_output


async def test_paged_search(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    expected_results = [mock_ldap_response(ldap_attributes, dn)]

    # Mock LDAP connection
    ldap_connection.response = expected_results

    # Simulate three pages
    cookies = [bytes("first page", "utf-8"), bytes("second page", "utf-8"), None]
    results = iter(
        [
            {
                "controls": {"1.2.840.113556.1.4.319": {"value": {"cookie": cookie}}},
                "description": "OK",
            }
            for cookie in cookies
        ]
    )

    def set_new_result(*args, **kwargs) -> None:
        ldap_connection.result = next(results)

    # Every time a search is performed, point to the next page.
    ldap_connection.search.side_effect = set_new_result

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    output = paged_search(context, searchParameters)

    assert output == expected_results * len(cookies)


async def test_invalid_paged_search(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    ldap_connection.response = [mock_ldap_response(ldap_attributes, dn)]

    ldap_connection.result = {
        "description": "operationsError",
    }

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    output = paged_search(context, searchParameters)

    assert output == []


async def test_single_object_search(ldap_connection: MagicMock):

    search_entry = {"type": "searchResEntry"}

    ldap_connection.response = [search_entry]
    output = single_object_search({}, ldap_connection)

    assert output == search_entry
    ldap_connection.response = [search_entry]

    with pytest.raises(MultipleObjectsReturnedException):
        ldap_connection.response = [search_entry] * 2
        output = single_object_search({}, ldap_connection)

    with pytest.raises(NoObjectsReturnedException):
        ldap_connection.response = [search_entry] * 0
        output = single_object_search({}, ldap_connection)
