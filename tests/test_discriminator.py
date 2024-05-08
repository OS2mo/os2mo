# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Any
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastramqpi.ramqp.depends import Context
from fastramqpi.ramqp.utils import RequeueMessage
from ldap3 import BASE
from ldap3 import Connection
from ldap3 import MOCK_SYNC
from ldap3 import SUBTREE
from more_itertools import one
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.customer_specific_checks import ExportChecks
from mo_ldap_import_export.customer_specific_checks import ImportChecks
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server_pool
from mo_ldap_import_export.ldap import first_included
from mo_ldap_import_export.ldap import get_ldap_object
from mo_ldap_import_export.types import DN
from tests.graphql_mocker import GraphQLMocker


@pytest.fixture
def settings(minimal_valid_environmental_variables: None) -> Settings:
    return Settings()


@pytest.fixture
def ldap_container_dn() -> str:
    return "o=example"


@pytest.fixture
def ldap_connection(settings: Settings, ldap_container_dn: str) -> Iterable[Connection]:
    """Fixture to construct a mocked ldap_connection.

    Returns:
        The mocked configured ldap_connection.
    """
    # See https://ldap3.readthedocs.io/en/latest/mocking.html for details
    with patch(
        "mo_ldap_import_export.ldap.get_client_strategy", return_value=MOCK_SYNC
    ):
        # This patch is necessary due to: https://github.com/cannatag/ldap3/issues/1007
        server = one(construct_server_pool(settings).servers)
        with patch(
            "mo_ldap_import_export.ldap.construct_server_pool", return_value=server
        ):
            entryUUID = uuid4()

            ldap_connection = configure_ldap_connection(settings)
            ldap_connection.strategy.add_entry(
                f"CN={settings.ldap_user},{ldap_container_dn}",
                {
                    "objectClass": "inetOrgPerson",
                    "userPassword": settings.ldap_password.get_secret_value(),
                    "sn": f"{settings.ldap_user}_sn",
                    "revision": 0,
                    "entryUUID": "{" + str(entryUUID) + "}",
                    "employeeID": "0101700001",
                },
            )
            ldap_connection.bind()
            yield ldap_connection


@pytest.fixture
def ldap_dn(settings: Settings, ldap_container_dn: str) -> DN:
    return DN(f"CN={settings.ldap_user},{ldap_container_dn}")


async def test_searching_mocked(
    ldap_connection: Connection, settings: Settings, ldap_container_dn: str
) -> None:
    """Test that we can use the mocked ldap_connection to search for our default user."""
    ldap_connection.search(
        ldap_container_dn,
        f"(cn={settings.ldap_user})",
        search_scope=SUBTREE,
        attributes="*",
    )
    assert ldap_connection.result["description"] == "success"
    assert ldap_connection.response is not None
    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [settings.ldap_password.get_secret_value()],
            "sn": [f"{settings.ldap_user}_sn"],
            "revision": ["0"],
            "CN": [settings.ldap_user],
            "entryUUID": ANY,
            "employeeID": ["0101700001"],
        },
        "dn": f"CN={settings.ldap_user},{ldap_container_dn}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }


async def test_searching_newly_added(ldap_connection: Connection) -> None:
    """Test that we can use the mocked ldap_connection to find newly added users."""
    username = str(uuid4())
    password = str(uuid4())
    container = str(uuid4())
    entryUUID = str(uuid4())
    # Add new entry
    ldap_connection.strategy.add_entry(
        f"cn={username},o={container}",
        {
            "objectClass": "inetOrgPerson",
            "userPassword": password,
            "sn": f"{username}_sn",
            "revision": 1,
            "entryUUID": "{" + entryUUID + "}",
            "employeeID": "0101700002",
        },
    )

    ldap_connection.search(
        f"o={container}", f"(cn={username})", search_scope=SUBTREE, attributes="*"
    )
    assert ldap_connection.result["description"] == "success"
    assert ldap_connection.response is not None
    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [password],
            "sn": [f"{username}_sn"],
            "revision": ["1"],
            "CN": [username],
            "employeeID": ["0101700002"],
            "entryUUID": ANY,
        },
        "dn": f"cn={username},o={container}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }


async def test_searching_dn_lookup(
    ldap_connection: Connection, settings: Settings, ldap_dn: DN, ldap_container_dn: str
) -> None:
    """Test that we can read our default user."""
    ldap_connection.search(
        ldap_dn,
        "(objectclass=*)",
        attributes="*",
        search_scope=BASE,
    )
    assert ldap_connection.result["description"] == "success"
    assert ldap_connection.response is not None
    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [settings.ldap_password.get_secret_value()],
            "sn": [f"{settings.ldap_user}_sn"],
            "revision": ["0"],
            "CN": [settings.ldap_user],
            "entryUUID": ANY,
            "employeeID": ["0101700001"],
        },
        "dn": f"CN={settings.ldap_user},{ldap_container_dn}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }


@pytest.mark.parametrize(
    "attributes,expected",
    [
        # Reading 'None' reads all fields
        (
            None,
            {
                "CN": ["foo"],
                "objectClass": ["inetOrgPerson"],
                "revision": ["0"],
                "sn": ["foo_sn"],
                "userPassword": ["foo"],
                "employeeID": ["0101700001"],
                "entryUUID": ANY,
            },
        ),
        # Reading no fields reads dn
        ([], {}),
        # Read SN
        (["sn"], {"sn": ["foo_sn"]}),
        (["SN"], {"sn": ["foo_sn"]}),
        # Read CN
        (["cn"], {"CN": ["foo"]}),
        (["CN"], {"CN": ["foo"]}),
        # Read SN and CN
        (["sn", "cn"], {"sn": ["foo_sn"], "CN": ["foo"]}),
        (["sn", "CN"], {"sn": ["foo_sn"], "CN": ["foo"]}),
        # Read unknown field
        (["__invalid__"], {"__invalid__": []}),
    ],
)
async def test_get_ldap_object(
    ldap_connection: Connection,
    settings: Settings,
    ldap_dn: DN,
    attributes: list[str],
    expected: dict[str, Any],
) -> None:
    """Test that get_ldap_object can read specific attributes on our default user."""
    context: Context = {
        "user_context": {"ldap_connection": ldap_connection, "settings": settings}
    }

    result = get_ldap_object(
        ldap_dn, context, attributes=attributes, run_discriminator=False
    )
    assert result.dn == ldap_dn
    assert result.__dict__ == {"dn": "CN=foo,o=example"} | expected


async def test_get_ldap_cpr_object(
    ldap_connection: Connection,
    settings: Settings,
    ldap_container_dn: str,
) -> None:
    ldap_connection.search(
        ldap_container_dn,
        "(&(objectclass=inetOrgPerson)(employeeID=0101700001))",
        search_scope=SUBTREE,
        attributes="*",
    )
    assert ldap_connection.result["description"] == "success"
    assert ldap_connection.response is not None
    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [settings.ldap_password.get_secret_value()],
            "sn": [f"{settings.ldap_user}_sn"],
            "revision": ["0"],
            "CN": [settings.ldap_user],
            "entryUUID": ANY,
            "employeeID": ["0101700001"],
        },
        "dn": f"CN={settings.ldap_user},{ldap_container_dn}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }


async def test_first_included_no_config(
    ldap_connection: Connection, settings: Settings
) -> None:
    """Test that first_included only allows one DN when not configured."""
    context: Context = {
        "user_context": {"ldap_connection": ldap_connection, "settings": settings}
    }
    assert settings.discriminator_field is None

    with pytest.raises(ValueError) as exc_info:
        first_included(context, set())
    assert "too few items in iterable" in str(exc_info.value)

    result = first_included(context, {"CN=Anzu"})
    assert result == "CN=Anzu"

    with pytest.raises(ValueError) as exc_info:
        first_included(context, {"CN=Anzu", "CN=Arak"})
    assert "Expected exactly one item in iterable" in str(exc_info.value)


@pytest.mark.parametrize(
    "discriminator_settings",
    [
        # Needs function and values
        {
            "discriminator_field": "sn",
        },
        # Needs function
        {
            "discriminator_field": "sn",
            "discriminator_values": ["__never_gonna_match__"],
        },
        # Needs values
        {"discriminator_field": "sn", "discriminator_function": "exclude"},
        # Cannot give empty values
        {
            "discriminator_field": "sn",
            "discriminator_function": "exclude",
            "discriminator_values": [],
        },
        # Cannot give invalid function
        {
            "discriminator_field": "sn",
            "discriminator_function": "__invalid__",
            "discriminator_values": ["__never_gonna_match__"],
        },
    ],
)
async def test_first_included_settings_invariants(
    ldap_connection: Connection,
    settings: Settings,
    ldap_dn: DN,
    discriminator_settings: dict[str, Any],
) -> None:
    """Test that first_included checks settings invariants."""
    context: Context = {"user_context": {"ldap_connection": ldap_connection}}

    with pytest.raises(AssertionError):
        # Need function and values
        new_settings = settings.copy(update=discriminator_settings)
        context["user_context"]["settings"] = new_settings
        first_included(context, {ldap_dn})


async def test_first_included_unknown_dn(
    ldap_connection: Connection, settings: Settings
) -> None:
    """Test that first_included requeues on missing DNs."""
    settings = settings.copy(
        update={
            "discriminator_field": "sn",
            "discriminator_function": "exclude",
            "discriminator_values": ["__never_gonna_match__"],
        }
    )
    context: Context = {
        "user_context": {"ldap_connection": ldap_connection, "settings": settings}
    }
    with pytest.raises(RequeueMessage) as exc_info:
        first_included(context, {"CN=__missing__dn__"})
    assert "Unable to lookup DN(s)" in str(exc_info.value)


@pytest.mark.parametrize(
    "discriminator_values,matches",
    [
        # These do not contain foo_sn
        ([""], False),
        (["__never_gonna_match__"], False),
        (["__never_gonna_match__", "bar_sn"], False),
        (["bar_sn", "__never_gonna_match__"], False),
        # These contain foo_sn
        (["foo_sn"], True),
        (["__never_gonna_match__", "foo_sn"], True),
        (["foo_sn", "__never_gonna_match__"], True),
    ],
)
@pytest.mark.parametrize("discriminator_function", ("include", "exclude"))
async def test_first_included_exclude_one_user(
    ldap_connection: Connection,
    settings: Settings,
    ldap_dn: DN,
    discriminator_function: str,
    discriminator_values: list[str],
    matches: bool,
) -> None:
    """Test that first_included exclude works with a single user on valid settings."""
    # This DN has 'foo_sn' as their sn
    if discriminator_function == "include":
        expected = ldap_dn if matches else None
    else:
        expected = None if matches else ldap_dn

    settings = settings.copy(
        update={
            "discriminator_field": "sn",
            "discriminator_function": discriminator_function,
            "discriminator_values": discriminator_values,
        }
    )
    context: Context = {
        "user_context": {"ldap_connection": ldap_connection, "settings": settings}
    }
    result = first_included(context, {ldap_dn})
    assert result == expected


@pytest.fixture
async def sync_tool(
    ldap_connection: Connection,
    ldap_container_dn: str,
    settings: Settings,
    graphql_client: GraphQLClient,
    graphql_mock: GraphQLMocker,
) -> SyncTool:
    settings = settings.copy(
        update={
            "ldap_unique_id_field": "entryUUID",
            "ldap_search_base": ldap_container_dn,
        }
    )

    mapping = settings.conversion_mapping.dict(exclude_unset=True, by_alias=True)

    route = graphql_mock.query("read_facet_classes")
    route.result = {"classes": {"objects": []}}

    route = graphql_mock.query("read_itsystems")
    route.result = {"itsystems": {"objects": []}}

    route = graphql_mock.query("read_org_units")
    route.result = {"org_units": {"objects": []}}

    route = graphql_mock.query("read_class_user_keys")
    route.result = {"classes": {"objects": []}}

    context: Context = {
        "user_context": {
            "ldap_connection": ldap_connection,
            "settings": settings,
            "mapping": mapping,
            # TODO: This should be set by side-effect reference, no?
            "cpr_field": "employeeID",
            # TODO: This should be set by side-effect reference, no?
            "ldap_it_system_user_key": None,
        },
        "graphql_client": graphql_client,
        "amqpsystem": AsyncMock(),
    }
    # Needs context, user_context, ldap_connection
    with patch(
        "mo_ldap_import_export.dataloaders.get_attribute_types",
        return_value={
            "objectClass": MagicMock(),
            "employeeID": MagicMock(),
        },
    ):
        dataloader = DataLoader(context)
        dataloader.load_ldap_overview = MagicMock()  # type: ignore
        dataloader.load_ldap_overview.return_value = {
            "inetOrgPerson": {"attributes": {"employeeID": MagicMock()}}
        }
    context["user_context"]["dataloader"] = dataloader

    # Needs context, user_context, settings, raw_mapping, dataloader
    converter = LdapConverter(context)
    await converter._init()
    context["user_context"]["converter"] = converter

    # Needs context, user_context, dataloader, converter
    export_checks = ExportChecks(context)
    context["user_context"]["export_checks"] = export_checks
    # Needs context
    import_checks = ImportChecks(context)
    context["user_context"]["import_checks"] = import_checks

    # Needs context, user_context, dataloader, converter, export_checks, import_checks, settings, amqpsystem
    sync_tool = SyncTool(context)
    context["user_context"]["synctool"] = sync_tool

    return sync_tool


@pytest.fixture
def inject_environmental_variables(
    environmental_variables: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    with monkeypatch.context() as mpc:
        for key, value in environmental_variables.items():
            mpc.setenv(key, value)
        yield


@pytest.mark.parametrize(
    "environmental_variables,extra_account,log_lines",
    [
        # Discriminator not configured
        (
            {},
            False,
            [
                "UUID Not found",
                "Could not find engagement UUID for DN",
                "Engagement UUID not found in MO",
                "Import checks executed",
                "Import to MO filtered",
            ],
        ),
        # Discriminator rejecting all accounts
        (
            {
                "DISCRIMINATOR_FIELD": "sn",
                "DISCRIMINATOR_FUNCTION": "include",
                "DISCRIMINATOR_VALUES": '["__never_gonna_match__"]',
            },
            True,
            [
                "Found DN",
                "Aborting synchronization, as no good LDAP account was found",
            ],
        ),
        # Discriminator finding original account
        (
            {
                "DISCRIMINATOR_FIELD": "sn",
                "DISCRIMINATOR_FUNCTION": "include",
                "DISCRIMINATOR_VALUES": '["foo_sn"]',
            },
            True,
            [
                "Found DN",
                "Found DN",
                "UUID Not found",
                "Could not find engagement UUID for DN",
                "Engagement UUID not found in MO",
                "Import checks executed",
                "Import to MO filtered",
            ],
        ),
        # Discriminator finding another account
        (
            {
                "DISCRIMINATOR_FIELD": "sn",
                "DISCRIMINATOR_FUNCTION": "include",
                "DISCRIMINATOR_VALUES": '["bar_sn"]',
            },
            True,
            [
                "Found DN",
                "Found better DN for employee",
                "Found DN",
                "UUID Not found",
                "Could not find engagement UUID for DN",
                "Engagement UUID not found in MO",
                "Import checks executed",
                "Import to MO filtered",
            ],
        ),
    ],
)
@pytest.mark.usefixtures("inject_environmental_variables")
async def test_import_single_user_first_included(
    ldap_connection: Connection,
    ldap_container_dn: str,
    ldap_dn: DN,
    graphql_mock: GraphQLMocker,
    sync_tool: SyncTool,
    extra_account: bool,
    log_lines: list[str],
) -> None:
    if extra_account:
        another_username = "bar"
        ldap_connection.strategy.add_entry(
            f"CN={another_username},{ldap_container_dn}",
            {
                "objectClass": "inetOrgPerson",
                "userPassword": str(uuid4()),
                "sn": f"{another_username}_sn",
                "revision": 1,
                "entryUUID": "{" + str(uuid4()) + "}",
                "employeeID": "0101700001",
            },
        )

    route = graphql_mock.query("read_employee_uuid_by_ituser_user_key")
    route.result = {"itusers": {"objects": []}}

    employee_uuid = uuid4()

    route = graphql_mock.query("read_employee_uuid_by_cpr_number")
    route.result = {"employees": {"objects": [{"uuid": employee_uuid}]}}

    route = graphql_mock.query("read_employees")
    route.result = {
        "employees": {
            "objects": [
                {
                    "validities": [
                        {
                            "uuid": employee_uuid,
                            "cpr_no": "0101700001",
                            "givenname": "Chen",
                            "surname": "Stormstout",
                            "nickname_givenname": "Chen",
                            "nickname_surname": "Brewmaster",
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user(ldap_dn)
    events = [x["event"] for x in cap_logs]

    assert (
        events
        == [
            "Generating DN",
            "Importing user",
            "Found DN",
            "Found employee via CPR matching",
            "Attempting to find DNs",
            "UUID Not found",
            "Attempting CPR number lookup",
            "Found LDAP(s) object",
            "Found DN(s) using CPR number lookup",
            "Found DN",
        ]
        + log_lines
    )


@pytest.mark.parametrize(
    "environmental_variables,extra_account,log_lines",
    [
        # Discriminator not configured
        (
            {},
            False,
            [
                "Found Employee in MO",
                "_export_to_ldap_ == False.",
            ],
        ),
        # Discriminator rejecting all accounts
        (
            {
                "DISCRIMINATOR_FIELD": "sn",
                "DISCRIMINATOR_FUNCTION": "include",
                "DISCRIMINATOR_VALUES": '["__never_gonna_match__"]',
            },
            True,
            [
                "Found DN",
                "Found DN",
                "Aborting synchronization, as no good LDAP account was found",
            ],
        ),
        # Discriminator finding original account
        (
            {
                "DISCRIMINATOR_FIELD": "sn",
                "DISCRIMINATOR_FUNCTION": "include",
                "DISCRIMINATOR_VALUES": '["foo_sn"]',
            },
            True,
            [
                "Found DN",
                "Found DN",
                "Found Employee in MO",
                "_export_to_ldap_ == False.",
            ],
        ),
        # Discriminator finding another account
        (
            {
                "DISCRIMINATOR_FIELD": "sn",
                "DISCRIMINATOR_FUNCTION": "include",
                "DISCRIMINATOR_VALUES": '["bar_sn"]',
            },
            True,
            [
                "Found DN",
                "Found DN",
                "Found Employee in MO",
                "_export_to_ldap_ == False.",
            ],
        ),
    ],
)
@pytest.mark.usefixtures("inject_environmental_variables")
async def test_listen_to_changes_in_employees(
    ldap_connection: Connection,
    ldap_container_dn: str,
    ldap_dn: DN,
    graphql_mock: GraphQLMocker,
    sync_tool: SyncTool,
    extra_account: bool,
    log_lines: list[str],
) -> None:
    if extra_account:
        another_username = "bar"
        ldap_connection.strategy.add_entry(
            f"CN={another_username},{ldap_container_dn}",
            {
                "objectClass": "inetOrgPerson",
                "userPassword": str(uuid4()),
                "sn": f"{another_username}_sn",
                "revision": 1,
                "entryUUID": "{" + str(uuid4()) + "}",
                "employeeID": "0101700001",
            },
        )

    route = graphql_mock.query("read_employee_uuid_by_ituser_user_key")
    route.result = {"itusers": {"objects": []}}

    employee_uuid = uuid4()

    route = graphql_mock.query("read_employee_uuid_by_cpr_number")
    route.result = {"employees": {"objects": [{"uuid": employee_uuid}]}}

    route = graphql_mock.query("read_employees")
    route.result = {
        "employees": {
            "objects": [
                {
                    "validities": [
                        {
                            "uuid": employee_uuid,
                            "cpr_no": "0101700001",
                            "givenname": "Chen",
                            "surname": "Stormstout",
                            "nickname_givenname": "Chen",
                            "nickname_surname": "Brewmaster",
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(
            uuid=employee_uuid,
            object_uuid=employee_uuid,
            routing_key="person",
            delete=False,
            current_objects_only=True,
        )
    events = [x["event"] for x in cap_logs]

    assert (
        events
        == [
            "Generating UUID",
            "Registered change in an employee",
            "Attempting to find DNs",
            "UUID Not found",
            "Attempting CPR number lookup",
            "Found LDAP(s) object",
            "Found DN(s) using CPR number lookup",
            "Found DNs for user",
        ]
        + log_lines
    )
