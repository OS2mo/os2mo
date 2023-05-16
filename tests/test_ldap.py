#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 11:03:16 2022

@author: nick
"""
import asyncio
import datetime
import os
import re
import time
from collections.abc import Iterator
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ldap3 import Connection
from ldap3 import MOCK_SYNC
from ldap3 import Server
from more_itertools import collapse
from ramodels.mo.details.address import Address
from ramodels.mo.employee import Employee
from ramqp.mo.models import ObjectType
from ramqp.mo.models import PayloadType
from ramqp.mo.models import ServiceType
from structlog.testing import capture_logs

from .test_dataloaders import mock_ldap_response
from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.exceptions import TimeOutException
from mo_ldap_import_export.ldap import cleanup
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server
from mo_ldap_import_export.ldap import get_client_strategy
from mo_ldap_import_export.ldap import get_ldap_attributes
from mo_ldap_import_export.ldap import is_dn
from mo_ldap_import_export.ldap import is_guid
from mo_ldap_import_export.ldap import ldap_healthcheck
from mo_ldap_import_export.ldap import make_ldap_object
from mo_ldap_import_export.ldap import paged_search
from mo_ldap_import_export.ldap import poller_healthcheck
from mo_ldap_import_export.ldap import set_search_params_modify_timestamp
from mo_ldap_import_export.ldap import setup_poller
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
    monkeypatch.setenv("ADMIN_PASSWORD", "admin")
    monkeypatch.setenv("AUTHENTICATION_SECRET", "foo")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_LEVEL", "foo")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_TYPE", "foo")

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
        "ADMIN_PASSWORD": "admin",
        "AUTHENTICATION_SECRET": "foo",
        "DEFAULT_ORG_UNIT_LEVEL": "foo",
        "DEFAULT_ORG_UNIT_TYPE": "foo",
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


def test_configure_ldap_connection_timeout(
    load_settings_overrides: dict[str, str]
) -> None:

    ldap_controller = MagicMock()
    ldap_controller.timeout = 1

    settings = MagicMock()
    settings.ldap_controllers = [ldap_controller]

    def connection_mock(*args, **kwargs):
        time.sleep(2)
        return None

    with patch(
        "mo_ldap_import_export.ldap.get_client_strategy", return_value=MOCK_SYNC
    ), patch("mo_ldap_import_export.ldap.Connection", connection_mock), patch(
        "mo_ldap_import_export.ldap.construct_server", MagicMock()
    ), patch(
        "mo_ldap_import_export.ldap.ServerPool", MagicMock()
    ):
        with pytest.raises(TimeOutException):
            configure_ldap_connection(settings)


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
    assert is_dn("CN=Harry Styles,OU=Band,DC=Stage") is True
    assert is_dn("foo") is False
    assert is_dn("cn@foo.dk") is False  # This passes the 'safe_dn' test


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
    output = paged_search(context, searchParameters, search_base="foo")
    assert output == expected_results * len(cookies)


async def test_paged_search_no_results(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):

    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    expected_results: List[Dict] = []

    # Mock LDAP connection
    ldap_connection.response = expected_results

    results = iter(
        [
            {
                "result": 32,
                "description": "noSuchObject",
                "dn": dn,
                "message": "0000208D: NameErr: DSID-03100245, problem 2001 "
                f"(NO_OBJECT), data 0, best match of:\n\t'{dn}'\n\x00",
                "referrals": None,
                "type": "searchResDone",
            }
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

    assert output == expected_results


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

    dn = "CN=foo,DC=bar"
    search_entry = {"type": "searchResEntry", "dn": dn}

    ldap_connection.response = [search_entry]
    output = single_object_search({"search_base": "CN=foo,DC=bar"}, ldap_connection)

    assert output == search_entry
    ldap_connection.response = [search_entry]

    search_parameters = {
        "search_base": "CN=foo,DC=bar",
        "search_filter": "CPR=010101-1234",
    }

    with pytest.raises(MultipleObjectsReturnedException, match="010101-xxxx"):
        ldap_connection.response = [search_entry] * 2
        output = single_object_search(search_parameters, ldap_connection)

    with pytest.raises(NoObjectsReturnedException, match="010101-xxxx"):
        ldap_connection.response = [search_entry] * 0
        output = single_object_search(search_parameters, ldap_connection)

    ldap_connection.response = [search_entry]
    output = single_object_search({"search_base": "CN=foo,DC=bar"}, ldap_connection)
    assert output == search_entry
    output = single_object_search(
        {"search_base": "CN=moo,CN=foo,DC=bar"}, ldap_connection
    )
    assert output == search_entry
    with pytest.raises(NoObjectsReturnedException, match="010101-xxxx"):
        search_parameters["search_base"] = "CN=moo,DC=bar"
        output = single_object_search(
            search_parameters,
            ldap_connection,
            exact_dn_match=True,
        )


@pytest.fixture()
def dataloader() -> AsyncMock:
    dataloader = AsyncMock()
    dataloader.cleanup_attributes_in_ldap = MagicMock()
    dataloader.load_ldap_object = MagicMock()
    return dataloader


@pytest.fixture()
def converter() -> MagicMock:
    converter = MagicMock()
    converter.__export_to_ldap__ = MagicMock()
    converter.__export_to_ldap__.return_value = True

    def to_ldap(conversion_dict, json_key, dn):
        return LdapObject(
            dn="CN=foo", address=conversion_dict["mo_employee_address"].value
        )

    converter.to_ldap.side_effect = to_ldap
    converter.get_ldap_attributes.return_value = ["address"]

    return converter


@pytest.fixture()
def internal_amqpsystem() -> AsyncMock:
    internal_amqpsystem = AsyncMock()
    return internal_amqpsystem


@pytest.fixture()
def user_context(
    dataloader: AsyncMock, converter: MagicMock, internal_amqpsystem: AsyncMock
) -> dict:

    user_context = dict(
        dataloader=dataloader,
        converter=converter,
        internal_amqpsystem=internal_amqpsystem,
    )
    return user_context


async def test_cleanup(
    dataloader: AsyncMock,
    converter: MagicMock,
    internal_amqpsystem: AsyncMock,
    user_context: dict,
):

    # There is one address in MO
    mo_objects = [
        Address.from_simplified_fields(
            "addr1",
            uuid4(),
            "2021-01-01",
        )
    ]

    # but two in LDAP
    dataloader.load_ldap_object.return_value = LdapObject(
        dn="CN=foo", address=["addr1", "addr2"]
    )

    # We would expect one of the addresses in LDAP to be cleaned
    args = dict(
        json_key="Address",
        mo_dict_key="mo_employee_address",
        mo_objects=mo_objects,
        user_context=user_context,
        employee=Employee(cpr_no="0101011234"),
        object_type=ObjectType.ADDRESS,
        dn="CN=foo",
    )

    await asyncio.gather(cleanup(**args))  # type:ignore
    ldap_objects_to_clean = dataloader.cleanup_attributes_in_ldap.call_args_list
    assert len(ldap_objects_to_clean) == 1


async def test_cleanup_no_sync_required(
    dataloader: AsyncMock,
    converter: MagicMock,
    internal_amqpsystem: AsyncMock,
    user_context: dict,
):

    # There is one address in MO
    mo_objects = [
        Address.from_simplified_fields(
            "addr1",
            uuid4(),
            "2021-01-01",
        )
    ]

    # And it is also in LDAP
    dataloader.load_ldap_object.return_value = LdapObject(dn="CN=foo", address="addr1")

    # We would expect that no synchronization is required
    args = dict(
        json_key="Address",
        mo_dict_key="mo_employee_address",
        mo_objects=mo_objects,
        user_context=user_context,
        employee=Employee(cpr_no="0101011234"),
        object_type=ObjectType.ADDRESS,
        dn="CN=foo",
    )

    with capture_logs() as cap_logs:
        await asyncio.gather(cleanup(**args))  # type:ignore
        log_messages = [log for log in cap_logs if log["log_level"] == "info"]
        assert re.match(
            "No synchronization required",
            log_messages[-1]["event"],
        )


async def test_cleanup_refresh_mo_object(
    dataloader: AsyncMock,
    converter: MagicMock,
    internal_amqpsystem: AsyncMock,
    user_context: dict,
):

    # There is one address in MO
    mo_objects = [
        Address.from_simplified_fields(
            "addr1",
            uuid4(),
            "2021-01-01",
        )
    ]

    args = dict(
        json_key="Address",
        mo_dict_key="mo_employee_address",
        mo_objects=mo_objects,
        user_context=user_context,
        employee=Employee(cpr_no="0101011234"),
        object_type=ObjectType.ADDRESS,
        dn="CN=foo",
    )

    object_uuid = str(mo_objects[0].uuid)
    employee_uuid = str(uuid4())
    dataloader.load_mo_object.return_value = {
        "uuid": object_uuid,
        "service_type": ServiceType.EMPLOYEE,
        "payload": PayloadType(
            uuid=employee_uuid,
            object_uuid=object_uuid,
            time=datetime.datetime.now(),
        ),
        "object_type": ObjectType.ADDRESS,
        "validity": {
            "from": datetime.datetime.today().strftime("%Y-%m-%d"),
            "to": None,
        },
    }

    # And None in LDAP
    for none_val in [[], None, ""]:  # type: ignore
        dataloader.load_ldap_object.return_value = LdapObject(
            dn="CN=foo", address=none_val
        )

        # We would expect that an AMQP message is sent over the internal AMQP system
        await asyncio.gather(cleanup(**args))  # type:ignore

        messages = internal_amqpsystem.publish_message.await_args_list
        assert len(messages) == 1
        assert messages[0].args[0] == "employee.address.refresh"
        assert messages[0].args[1]["uuid"] == employee_uuid
        assert messages[0].args[1]["object_uuid"] == object_uuid

        internal_amqpsystem.publish_message.reset_mock()


async def test_cleanup_no_export_False(
    dataloader: AsyncMock,
    converter: MagicMock,
    internal_amqpsystem: AsyncMock,
    user_context: dict,
):
    converter.__export_to_ldap__.return_value = False

    args = dict(
        json_key="Address",
        mo_dict_key="mo_employee_address",
        mo_objects=[],
        user_context=user_context,
        employee=Employee(cpr_no="0101011234"),
        object_type=ObjectType.ADDRESS,
        dn="CN=foo",
    )

    with capture_logs() as cap_logs:
        await asyncio.gather(cleanup(**args))  # type:ignore
        log_messages = [log for log in cap_logs if log["log_level"] == "info"]
        assert re.match(
            "__export_to_ldap__ == False",
            log_messages[-1]["event"],
        )


async def test_set_search_params_modify_timestamp():
    for search_filter in ["(cn=*)", "cn=*"]:
        search_params = {
            "search_base": "foo",
            "search_filter": search_filter,
            "attributes": ["employeeID", "modifyTimestamp"],
        }
        timestamp = datetime.datetime(2021, 1, 1)

        modified_search_params = set_search_params_modify_timestamp(
            search_params,
            timestamp,
        )

        assert (
            modified_search_params["search_filter"]
            == "(&(modifyTimestamp>=20210101000000.0-0000)(cn=*))"
        )

        assert modified_search_params["search_base"] == search_params["search_base"]
        assert modified_search_params["attributes"] == search_params["attributes"]


async def test_setup_poller(context: Context):
    with patch("mo_ldap_import_export.ldap._poller", MagicMock()):

        def callback():
            return

        search_parameters: dict = {}
        init_search_time = datetime.datetime.utcnow()

        poll = setup_poller(context, callback, search_parameters, init_search_time, 5)
        assert poll._initialized is True  # type: ignore


def test_poller(
    load_settings_overrides: Dict[str, str], ldap_connection: MagicMock
) -> None:
    hits: List[str] = []

    def listener(event):
        cpr_no = event.get("attributes", {}).get("cpr_no", None)
        hits.append(cpr_no)

    event = {
        "type": "searchResEntry",
        "attributes": {
            "modifyTimeStamp": datetime.datetime.utcnow(),
            "cpr_no": "010101-1234",
        },
    }
    ldap_connection.response = [event]

    setup_poller(
        context={"user_context": {"ldap_connection": ldap_connection}},
        callback=listener,
        search_parameters={
            "search_base": "dc=ad",
            "search_filter": "cn=*",
            "attributes": ["cpr_no"],
        },
        init_search_time=datetime.datetime.utcnow(),
        poll_time=0.1,
    )
    time.sleep(0.15)
    assert hits == ["010101-1234"]


def test_poller_invalidQuery(
    load_settings_overrides: Dict[str, str], ldap_connection: MagicMock
) -> None:
    def listener(event):
        pass

    # Event without modifyTimeStamp makes it impossible to determine if it
    # is duplicate - so we expect a warning
    event = {
        "type": "searchResEntry",
        "attributes": {
            "cpr_no": "010101-1234",
        },
    }
    ldap_connection.response = [event]

    with capture_logs() as cap_logs:
        setup_poller(
            context={"user_context": {"ldap_connection": ldap_connection}},
            callback=listener,
            search_parameters={
                "search_base": "dc=ad",
                "search_filter": "cn=*",
                "attributes": ["cpr_no"],
            },
            init_search_time=datetime.datetime.utcnow(),
            poll_time=0.1,
        )
        time.sleep(0.15)

        log_messages = [log for log in cap_logs if log["log_level"] == "warning"]

        assert re.match(
            ".*modifyTimeStamp' not found.*",
            log_messages[-1]["event"],
        )


def test_is_guid():
    assert is_guid(str(uuid4())) is True
    assert is_guid("not_an_uuid") is False
    assert is_guid(None) is False
    assert is_guid(uuid4()) is True


async def test_poller_healthcheck():
    poller = MagicMock()
    poller.is_alive.return_value = False
    assert (await poller_healthcheck({"user_context": {"pollers": [poller]}})) is False

    poller.is_alive.return_value = True
    assert (await poller_healthcheck({"user_context": {"pollers": [poller]}})) is True

    second_poller = MagicMock()
    second_poller.is_alive.return_value = False
    pollers = [poller, second_poller]

    assert (await poller_healthcheck({"user_context": {"pollers": pollers}})) is False
