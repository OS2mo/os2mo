# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import datetime
import os
import time
from collections.abc import Iterator
from contextlib import suppress
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import ldap3.core.exceptions
import pytest
from fastramqpi.context import Context
from ldap3 import MOCK_SYNC
from ldap3 import Connection
from ldap3 import Server
from more_itertools import collapse
from pydantic import parse_obj_as
from structlog.testing import capture_logs

from mo_ldap_import_export.config import AuthBackendEnum
from mo_ldap_import_export.config import ConversionMapping
from mo_ldap_import_export.config import ServerConfig
from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.exceptions import TimeOutException
from mo_ldap_import_export.ldap import check_ou_in_list_of_ous
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server
from mo_ldap_import_export.ldap import get_client_strategy
from mo_ldap_import_export.ldap import is_dn
from mo_ldap_import_export.ldap import is_uuid
from mo_ldap_import_export.ldap import ldap_healthcheck
from mo_ldap_import_export.ldap import make_ldap_object
from mo_ldap_import_export.ldap import paged_search
from mo_ldap_import_export.ldap import single_object_search
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.ldap_event_generator import LDAPEventGenerator
from mo_ldap_import_export.ldap_event_generator import _poll
from mo_ldap_import_export.ldap_event_generator import setup_poller
from mo_ldap_import_export.routes import get_attribute_types
from mo_ldap_import_export.routes import get_ldap_attributes

from .test_dataloaders import mock_ldap_response


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
def settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        '{"ldap_to_mo": {}, "username_generator": {}}',
    )
    monkeypatch.setenv("CLIENT_ID", "foo")
    monkeypatch.setenv("CLIENT_SECRET", "bar")
    monkeypatch.setenv("LDAP_CONTROLLERS", '[{"host": "0.0.0.0"}]')
    monkeypatch.setenv("LDAP_DOMAIN", "LDAP")
    monkeypatch.setenv("LDAP_USER", "foo")
    monkeypatch.setenv("LDAP_PASSWORD", "bar")
    monkeypatch.setenv("LDAP_SEARCH_BASE", "DC=ad,DC=addev")
    monkeypatch.setenv("LDAP_OBJECT_CLASS", "inetOrgPerson")
    monkeypatch.setenv("LDAP_CPR_ATTRIBUTE", "employeeNumber")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_LEVEL", "foo")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_TYPE", "foo")
    monkeypatch.setenv("FASTRAMQPI__AMQP__URL", "amqp://guest:guest@msg_broker:5672/")
    monkeypatch.setenv("INTERNAL_AMQP__URL", "amqp://guest:guest@msg_broker:5672/")

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
    settings: Settings,
    cpr_field: str,
) -> Context:
    return {
        "user_context": {
            "settings": settings,
            "ldap_connection": ldap_connection,
            "gql_client": gql_client,
            "cpr_field": cpr_field,
        },
    }


@pytest.fixture
def settings_overrides() -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings.

    Yields:
        Minimal set of overrides.
    """
    conversion_mapping_dict = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "Employee",
                "_import_to_mo_": "false",
                "_ldap_attributes_": [],
                "uuid": "{{ employee_uuid or '' }}",
            }
        },
        "username_generator": {"objectClass": "UserNameGenerator"},
    }
    conversion_mapping = parse_obj_as(ConversionMapping, conversion_mapping_dict)
    conversion_mapping_setting = conversion_mapping.json(
        exclude_unset=True, by_alias=True
    )
    overrides = {
        "CONVERSION_MAPPING": conversion_mapping_setting,
        "LDAP_CONTROLLERS": '[{"host": "111.111.111.111"}]',
        "CLIENT_ID": "foo",
        "CLIENT_SECRET": "bar",
        "LDAP_DOMAIN": "LDAP",
        "LDAP_USER": "foo",
        "LDAP_PASSWORD": "foo",
        "LDAP_SEARCH_BASE": "DC=ad,DC=addev",
        "LDAP_OBJECT_CLASS": "inetOrgPerson",
        "LDAP_CPR_ATTRIBUTE": "employeeNumber",
        "DEFAULT_ORG_UNIT_LEVEL": "foo",
        "DEFAULT_ORG_UNIT_TYPE": "foo",
        "FASTRAMQPI__AMQP__URL": "amqp://guest:guest@msg_broker:5672/",
        "INTERNAL_AMQP__URL": "amqp://guest:guest@msg_broker:5672/",
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
    load_settings_overrides: dict[str, str],
) -> None:
    ldap_controller = MagicMock()
    ldap_controller.timeout = 1

    settings = MagicMock()
    settings.ldap_auth_method = AuthBackendEnum.NTLM
    settings.ldap_controllers = [ldap_controller]

    def connection_mock(*args, **kwargs):
        time.sleep(2)
        return None

    with (
        patch("mo_ldap_import_export.ldap.get_client_strategy", return_value=MOCK_SYNC),
        patch("mo_ldap_import_export.ldap.Connection", connection_mock),
        patch("mo_ldap_import_export.ldap.construct_server", MagicMock()),
        patch("mo_ldap_import_export.ldap.ServerPool", MagicMock()),
        pytest.raises(TimeOutException),
    ):
        configure_ldap_connection(settings)


def test_configure_ldap_connection_simple(
    load_settings_overrides: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ldap_auth_method", "simple")
    settings = Settings()

    reason = "Error binding to server: {}".format("BOOM")

    def connection_mock(*args, **kwargs):
        raise ldap3.core.exceptions.LDAPBindError(reason)

    with (
        capture_logs() as cap_logs,
        patch("mo_ldap_import_export.ldap.get_client_strategy", return_value=MOCK_SYNC),
        patch("mo_ldap_import_export.ldap.Connection", connection_mock),
        pytest.raises(ldap3.core.exceptions.LDAPBindError),
    ):
        configure_ldap_connection(settings)

    assert "Connecting to server" in str(cap_logs)
    assert "'auth_strategy': 'simple'" in str(cap_logs)


def test_configure_ldap_connection_unknown(
    load_settings_overrides: dict[str, str],
) -> None:
    ldap_controller = ServerConfig(host="0.0.0.0")

    invalid_auth_method = MagicMock()
    invalid_auth_method.value = "invalid"

    settings = MagicMock()
    settings.ldap_auth_method = invalid_auth_method
    settings.ldap_controllers = [ldap_controller]

    with pytest.raises(ValueError) as exc_info:
        configure_ldap_connection(settings)
    assert "Unknown authentication backend" in str(exc_info.value)


def test_get_client_strategy() -> None:
    strategy = get_client_strategy()
    assert strategy == "ASYNC"


@pytest.mark.parametrize("bound", [True, False])
@pytest.mark.parametrize("listening", [True, False])
@pytest.mark.parametrize("closed", [True, False])
@pytest.mark.parametrize("result_type", ["searchResDone", "operationsError"])
@pytest.mark.parametrize("description", ["success", "failure"])
async def test_ldap_healthcheck(
    ldap_connection: MagicMock,
    bound: bool,
    listening: bool,
    closed: bool,
    result_type: str,
    description: str,
) -> None:
    result = {"type": result_type, "description": description}

    ldap_connection.get_response.return_value = [{}], result
    ldap_connection.bound = bound
    ldap_connection.listening = listening
    ldap_connection.closed = closed
    context = {"user_context": {"ldap_connection": ldap_connection}}

    check = await ldap_healthcheck(context)
    all_ok = (
        bound
        and listening
        and not closed
        and result_type == "searchResDone"
        and description == "success"
    )
    assert check == all_ok


async def test_ldap_healthcheck_exception(ldap_connection: MagicMock) -> None:
    ldap_connection.get_response.side_effect = ValueError("BOOM")
    ldap_connection.bound = True
    ldap_connection.listening = True
    ldap_connection.closed = False

    context = {"user_context": {"ldap_connection": ldap_connection}}

    check = await ldap_healthcheck(context)
    assert check is False


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

    ldap_connection = context["user_context"]["ldap_connection"]
    ldap_object = await make_ldap_object(response, ldap_connection, nest=False)

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
        ldap_connection = context["user_context"]["ldap_connection"]
        ldap_object = await make_ldap_object(response, ldap_connection, nest=True)

    # harry is an Employee because he has a cpr no.
    assert isinstance(ldap_object, LdapObject)

    # The manager is generic because she does not have a cpr no.
    assert isinstance(ldap_object.manager, LdapObject)  # type: ignore

    # The manager's buddies are dns because we only nest 1 level
    assert is_dn(ldap_object.manager.best_friend) is True  # type: ignore
    assert is_dn(ldap_object.manager.buddies[0]) is True  # type: ignore
    assert is_dn(ldap_object.manager.buddies[1]) is True  # type: ignore

    # The band members are generic because they do not have a cpr no.
    assert isinstance(ldap_object.band_members, list)  # type: ignore
    assert isinstance(ldap_object.band_members[0], LdapObject)  # type: ignore
    assert isinstance(ldap_object.band_members[1], LdapObject)  # type: ignore


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
        ldap_connection.get_response.return_value = expected_results, next(results)

    # Every time a search is performed, point to the next page.
    ldap_connection.search.side_effect = set_new_result

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    settings = context["user_context"]["settings"]
    output = await paged_search(
        settings, ldap_connection, searchParameters, search_base="foo"
    )
    assert output == expected_results * len(cookies)


async def test_paged_search_no_results(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):
    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    expected_results: list[dict] = []

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
        ldap_connection.get_response.return_value = expected_results, next(results)

    # Every time a search is performed, point to the next page.
    ldap_connection.search.side_effect = set_new_result

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    settings = context["user_context"]["settings"]
    output = await paged_search(settings, ldap_connection, searchParameters)

    assert output == expected_results


async def test_invalid_paged_search(
    context: Context, ldap_attributes: dict, ldap_connection: MagicMock
):
    # Mock data
    dn = "CN=Nick Janssen,OU=Users,OU=Magenta,DC=ad,DC=addev"

    response = [mock_ldap_response(ldap_attributes, dn)]
    result = {
        "description": "operationsError",
    }
    ldap_connection.get_response.return_value = response, result

    searchParameters = {
        "search_filter": "(objectclass=organizationalPerson)",
        "attributes": ["foo", "bar"],
    }
    settings = context["user_context"]["settings"]
    output = await paged_search(settings, ldap_connection, searchParameters)

    assert output == []


async def test_single_object_search(ldap_connection: MagicMock, context: Context):
    dn = "CN=foo,DC=bar"
    search_entry = {"type": "searchResEntry", "dn": dn}

    result = {"type": "test"}

    ldap_connection.get_response.return_value = [search_entry], result
    output = await single_object_search(
        {"search_base": "CN=foo,DC=bar"}, ldap_connection
    )

    assert output == search_entry
    ldap_connection.get_response.return_value = [search_entry], result

    search_parameters = {
        "search_base": "CN=foo,DC=bar",
        "search_filter": "CPR=010101-1234",
    }

    with pytest.raises(MultipleObjectsReturnedException, match="010101-1234"):
        ldap_connection.get_response.return_value = [search_entry] * 2, result
        await single_object_search(search_parameters, ldap_connection)

    with pytest.raises(NoObjectsReturnedException, match="010101-1234"):
        ldap_connection.get_response.return_value = [search_entry] * 0, result
        await single_object_search(search_parameters, ldap_connection)

    ldap_connection.get_response.return_value = [search_entry], result
    output = await single_object_search(
        {"search_base": "CN=foo,DC=bar"}, ldap_connection
    )
    assert output == search_entry
    output = await single_object_search(
        {"search_base": "CN=moo,CN=foo,DC=bar"}, ldap_connection
    )
    assert output == search_entry


async def test_setup_poller() -> None:
    async def _poller(*args: Any) -> None:
        raise ValueError("BOOM")

    settings = MagicMock()
    ldap_amqpsystem = AsyncMock()
    sessionmaker = AsyncMock()
    ldap_connection = AsyncMock()

    with patch("mo_ldap_import_export.ldap_event_generator._poller", _poller):
        search_base = "dc=magenta,dc=dk"

        handle = setup_poller(
            settings, ldap_amqpsystem, ldap_connection, sessionmaker, search_base
        )

        assert handle.done() is False

        # Give it a chance to run and explode
        await asyncio.sleep(0)
        assert handle.done() is True

        # Check that it exploded
        with pytest.raises(ValueError) as exc_info:
            handle.result()
        assert "BOOM" in str(exc_info.value)


async def test_poller(
    load_settings_overrides: dict[str, str], ldap_connection: MagicMock
) -> None:
    settings = Settings()

    uuid = uuid4()
    event = {
        "type": "searchResEntry",
        "attributes": {settings.ldap_unique_id_field: str(uuid)},
    }
    ldap_connection.get_response.return_value = (
        [event],
        {
            "type": "searchResEntry",
            "description": "success",
        },
    )

    last_search_time = datetime.datetime.now(datetime.UTC)
    uuids = await _poll(
        ldap_connection=ldap_connection,
        search_base="dc=ad",
        ldap_unique_id_field=settings.ldap_unique_id_field,
        last_search_time=last_search_time,
    )
    assert uuids == {uuid}


async def test_poller_no_uuid(
    load_settings_overrides: dict[str, str], ldap_connection: MagicMock
) -> None:
    event = {
        "type": "searchResEntry",
        "attributes": {},
    }
    ldap_connection.get_response.return_value = (
        [event],
        {
            "type": "searchResEntry",
            "description": "success",
        },
    )

    last_search_time = datetime.datetime.now(datetime.UTC)
    with capture_logs() as cap_logs:
        uuids = await _poll(
            ldap_connection=ldap_connection,
            search_base="dc=ad",
            ldap_unique_id_field="entryUUID",
            last_search_time=last_search_time,
        )
        assert uuids == set()
    assert {
        "event": "Got event without uuid",
        "log_level": "warning",
    } in cap_logs


@pytest.mark.parametrize(
    "response",
    [
        [],
        [{"type": "NOT_searchResEntry"}],
    ],
)
async def test_poller_bad_result(
    load_settings_overrides: dict[str, str], ldap_connection: MagicMock, response: Any
) -> None:
    ldap_connection.get_response.return_value = (
        response,
        {
            "type": "searchResEntry",
            "description": "success",
        },
    )

    ldap_amqpsystem = AsyncMock()

    last_search_time = datetime.datetime.now(datetime.UTC)
    await _poll(
        ldap_connection=ldap_connection,
        search_base="dc=ad",
        ldap_unique_id_field="entryUUID",
        last_search_time=last_search_time,
    )
    assert ldap_amqpsystem.call_count == 0


def test_is_uuid():
    assert is_uuid(str(uuid4())) is True
    assert is_uuid("not_an_uuid") is False
    assert is_uuid(None) is False
    assert is_uuid(uuid4()) is True


@pytest.mark.parametrize(
    "running,expected",
    [
        # No pollers
        ([], True),
        # One poller
        ([False], False),
        ([True], True),
        # Two pollers
        ([False, False], False),
        ([False, True], False),
        ([True, False], False),
        ([True, True], True),
    ],
)
async def test_poller_healthcheck(running: list[bool], expected: bool) -> None:
    async def waiter(event: asyncio.Event) -> None:
        await event.wait()

    events = [asyncio.Event() for _ in running]
    pollers = {asyncio.create_task(waiter(event)) for event in events}
    await asyncio.sleep(0)

    # Set events
    for event, is_running in zip(events, running, strict=False):
        if not is_running:
            event.set()
    await asyncio.sleep(0)

    sessionmaker = AsyncMock()
    settings = MagicMock()
    ldap_amqpsystem = AsyncMock()
    ldap_connection = MagicMock()
    ldap_event_generator = LDAPEventGenerator(
        sessionmaker, settings, ldap_amqpsystem, ldap_connection
    )
    ldap_event_generator._pollers = pollers

    context: Context = MagicMock()
    assert (await ldap_event_generator.healthcheck(context)) is expected

    # Signal all pollers to run
    for event in events:
        event.set()
    # Wait for all pollers to be shutdown
    for poller in pollers:
        with suppress(asyncio.CancelledError):
            await poller


def test_check_ou_in_list_of_ous():
    ous = ["OU=mucki,OU=bar", "OU=foo"]

    check_ou_in_list_of_ous("OU=foo", ous)
    check_ou_in_list_of_ous("OU=fighters,OU=foo", ous)
    check_ou_in_list_of_ous("OU=mucki,OU=bar", ous)
    with pytest.raises(ValueError):
        check_ou_in_list_of_ous("OU=bar", ous)
    with pytest.raises(ValueError):
        check_ou_in_list_of_ous("OU=foo fighters", ous)


def test_get_attribute_types():
    ldap_connection = MagicMock()
    ldap_connection.server.schema.attribute_types = ["a1", "a2"]
    assert get_attribute_types(ldap_connection) == ["a1", "a2"]
