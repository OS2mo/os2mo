# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from collections.abc import AsyncIterator
from collections.abc import Iterable
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
from ldap3 import MOCK_SYNC
from ldap3 import SUBTREE
from ldap3 import Connection
from more_itertools import one
from pydantic import parse_obj_as
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.customer_specific_checks import ExportChecks
from mo_ldap_import_export.customer_specific_checks import ImportChecks
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.ldap import apply_discriminator
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server_pool
from mo_ldap_import_export.ldap import get_ldap_object
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.main import GRAPHQL_VERSION
from mo_ldap_import_export.moapi import MOAPI
from mo_ldap_import_export.routes import load_ldap_OUs
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.usernames import UserNameGenerator
from mo_ldap_import_export.utils import extract_ou_from_dn
from tests.graphql_mocker import GraphQLMocker


@pytest.fixture
async def graphql_client() -> AsyncIterator[GraphQLClient]:
    # NOTE: We could have this session-scoped as it is essentially stateless
    async with GraphQLClient(
        f"http://example.com/graphql/v{GRAPHQL_VERSION}"
    ) as graphql_client:
        yield graphql_client


@pytest.fixture
def settings(
    minimal_valid_environmental_variables: None,
    monkeypatch: pytest.MonkeyPatch,
) -> Settings:
    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "false",
                        "_ldap_attributes_": ["employeeID"],
                        "cpr_number": "{{ldap.employeeID or None}}",
                        "uuid": "{{ employee_uuid or '' }}",
                    }
                },
                "mo2ldap": """
                {}
                """,
            }
        ),
    )

    return Settings()


@pytest.fixture
def ldap_container_dn() -> str:
    return "o=example"


@pytest.fixture
def ldap_connection(settings: Settings, ldap_container_dn: DN) -> Iterable[Connection]:
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
            # Undocumented hack to imitate SAFE strategies
            # See: https://github.com/cannatag/ldap3/issues/951
            # And: https://github.com/cannatag/ldap3/blob/dev/ldap3/strategy/safeSync.py
            ldap_connection.strategy.thread_safe = True
            # Create connection and yield it
            ldap_connection.bind()
            yield ldap_connection


@pytest.fixture
def ldap_api(settings: Settings, ldap_connection: Connection) -> LDAPAPI:
    return LDAPAPI(settings, ldap_connection)


@pytest.fixture
def ldap_dn(settings: Settings, ldap_container_dn: DN) -> DN:
    return DN(f"CN={settings.ldap_user},{ldap_container_dn}")


async def test_searching_mocked(
    ldap_api: LDAPAPI, settings: Settings, ldap_container_dn: DN
) -> None:
    """Test that we can use the mocked ldap_connection to search for our default user."""
    connection = ldap_api.ldap_connection
    response, result = await connection.ldap_search(
        search_base=ldap_container_dn,
        search_filter=f"(cn={settings.ldap_user})",
        search_scope=SUBTREE,
        attributes="*",
    )

    assert result["description"] == "success"
    assert response is not None
    search_result = one(response)
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


async def test_searching_newly_added(ldap_api: LDAPAPI) -> None:
    """Test that we can use the mocked ldap_connection to find newly added users."""
    username = str(uuid4())
    password = str(uuid4())
    container = str(uuid4())
    entryUUID = str(uuid4())
    # Add new entry
    ldap_api.ldap_connection.connection.strategy.add_entry(
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

    connection = ldap_api.ldap_connection
    response, result = await connection.ldap_search(
        search_base=f"o={container}",
        search_filter=f"(cn={username})",
        search_scope=SUBTREE,
        attributes="*",
    )

    assert result["description"] == "success"
    assert response is not None
    search_result = one(response)
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
    ldap_api: LDAPAPI, settings: Settings, ldap_dn: DN, ldap_container_dn: DN
) -> None:
    """Test that we can read our default user."""
    connection = ldap_api.ldap_connection
    response, result = await connection.ldap_search(
        search_base=ldap_dn,
        search_filter="(objectclass=*)",
        attributes="*",
        search_scope=BASE,
    )

    assert result["description"] == "success"
    assert response is not None
    search_result = one(response)
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
        (set(), {}),
        # Read SN
        ({"sn"}, {"sn": ["foo_sn"]}),
        ({"SN"}, {"sn": ["foo_sn"]}),
        # Read CN
        ({"cn"}, {"CN": ["foo"]}),
        ({"CN"}, {"CN": ["foo"]}),
        # Read SN and CN
        ({"sn", "cn"}, {"sn": ["foo_sn"], "CN": ["foo"]}),
        ({"sn", "CN"}, {"sn": ["foo_sn"], "CN": ["foo"]}),
        # Read unknown field
        ({"__invalid__"}, {"__invalid__": []}),
    ],
)
async def test_get_ldap_object(
    ldap_connection: Connection,
    ldap_dn: DN,
    attributes: set[str] | None,
    expected: dict[str, Any],
) -> None:
    """Test that get_ldap_object can read specific attributes on our default user."""
    result = await get_ldap_object(ldap_connection, ldap_dn, attributes=attributes)
    assert result.dn == ldap_dn
    assert result.__dict__ == {"dn": "CN=foo,o=example"} | expected


async def test_get_ldap_cpr_object(
    ldap_api: LDAPAPI,
    settings: Settings,
    ldap_container_dn: DN,
) -> None:
    connection = ldap_api.ldap_connection
    response, result = await connection.ldap_search(
        search_base=ldap_container_dn,
        search_filter="(&(objectclass=inetOrgPerson)(employeeID=0101700001))",
        search_scope=SUBTREE,
        attributes="*",
    )

    assert result["description"] == "success"
    assert response is not None
    search_result = one(response)
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


async def test_apply_discriminator_no_config(
    ldap_connection: Connection, settings: Settings
) -> None:
    """Test that apply_discriminator only allows one DN when not configured."""
    assert settings.discriminator_fields == []

    result = await apply_discriminator(settings, ldap_connection, set())
    assert result is None

    result = await apply_discriminator(settings, ldap_connection, {"CN=Anzu"})
    assert result == "CN=Anzu"

    with pytest.raises(ValueError) as exc_info:
        await apply_discriminator(settings, ldap_connection, {"CN=Anzu", "CN=Arak"})
    assert "Expected exactly one item in iterable" in str(exc_info.value)


@pytest.mark.parametrize(
    "discriminator_settings",
    [
        # Needs values
        {"discriminator_fields": ["sn"]},
        # Cannot give empty values
        {
            "discriminator_fields": ["sn"],
            "discriminator_values": [],
        },
    ],
)
async def test_apply_discriminator_settings_invariants(
    ldap_connection: Connection,
    settings: Settings,
    ldap_dn: DN,
    discriminator_settings: dict[str, Any],
) -> None:
    """Test that apply_discriminator checks settings invariants."""
    with pytest.raises(AssertionError):
        # Need values
        new_settings = settings.copy(update=discriminator_settings)
        await apply_discriminator(new_settings, ldap_connection, {ldap_dn})


async def test_apply_discriminator_unknown_dn(
    monkeypatch: pytest.MonkeyPatch, ldap_connection: Connection
) -> None:
    """Test that apply_discriminator requeues on missing DNs."""
    monkeypatch.setenv("DISCRIMINATOR_FIELDS", '["sn"]')
    monkeypatch.setenv("DISCRIMINATOR_VALUES", '["__never_gonna_match__"]')
    settings = Settings()
    with pytest.raises(RequeueMessage) as exc_info:
        await apply_discriminator(settings, ldap_connection, {"CN=__missing__dn__"})
    assert "Unable to lookup DN(s)" in str(exc_info.value)


async def test_apply_discriminator_missing_field(
    monkeypatch: pytest.MonkeyPatch,
    ldap_connection: Connection,
    ldap_container_dn: DN,
) -> None:
    """Test that apply_discriminator works with a single user on valid settings."""
    another_username = "bar"
    another_ldap_dn = f"CN={another_username},{ldap_container_dn}"
    ldap_connection.strategy.add_entry(
        another_ldap_dn,
        {
            "objectClass": "inetOrgPerson",
            "userPassword": str(uuid4()),
            "revision": 1,
            "entryUUID": "{" + str(uuid4()) + "}",
            "employeeID": "0101700001",
        },
    )

    monkeypatch.setenv("DISCRIMINATOR_FIELDS", '["hkOS2MOSync"]')
    monkeypatch.setenv("DISCRIMINATOR_VALUES", '["No"]')

    settings = Settings()
    with capture_logs() as cap_logs:
        result = await apply_discriminator(settings, ldap_connection, {another_ldap_dn})
        assert "Discriminator value is None" in (x["event"] for x in cap_logs)
    assert result is None


@pytest.fixture
async def sync_tool_and_context(
    ldap_connection: Connection,
    ldap_container_dn: DN,
    settings: Settings,
    graphql_client: GraphQLClient,
    graphql_mock: GraphQLMocker,
) -> tuple[SyncTool, Context]:
    settings = settings.copy(
        update={
            "ldap_unique_id_field": "entryUUID",
            "ldap_search_base": ldap_container_dn,
        }
    )

    route = graphql_mock.query("read_facet_classes")
    route.result = {"classes": {"objects": []}}

    route = graphql_mock.query("read_itsystems")
    route.result = {"itsystems": {"objects": []}}

    route = graphql_mock.query("read_org_units")
    route.result = {"org_units": {"objects": []}}

    context: Context = {
        "user_context": {
            "ldap_connection": ldap_connection,
            "settings": settings,
        },
        "graphql_client": graphql_client,
    }
    moapi = MOAPI(settings, graphql_client)

    username_generator = UserNameGenerator(settings, ldap_connection)
    context["user_context"]["username_generator"] = username_generator

    # Needs context, user_context, ldap_connection
    dataloader = DataLoader(
        settings, moapi, LDAPAPI(settings, ldap_connection), username_generator
    )
    context["user_context"]["dataloader"] = dataloader

    # Needs context, user_context, settings, raw_mapping, dataloader
    converter = LdapConverter(settings, dataloader, MagicMock())
    context["user_context"]["converter"] = converter

    export_checks = ExportChecks(dataloader)
    import_checks = ImportChecks()

    sync_tool = SyncTool(
        dataloader, converter, export_checks, import_checks, settings, ldap_connection
    )
    context["user_context"]["synctool"] = sync_tool

    return sync_tool, context


@pytest.fixture
async def sync_tool(sync_tool_and_context: tuple[SyncTool, Context]) -> SyncTool:
    return sync_tool_and_context[0]


@pytest.fixture
async def context(sync_tool_and_context: tuple[SyncTool, Context]) -> Context:
    return sync_tool_and_context[1]


@pytest.mark.parametrize(
    "extra_account,log_lines",
    [
        # Discriminator not configured
        pytest.param(
            False,
            [
                "Import to MO filtered",
                "Import checks executed",
            ],
            marks=pytest.mark.envvar({}),
        ),
        # Discriminator rejecting all accounts
        pytest.param(
            True,
            [
                "Found DN",
                "Found DN",
                "Aborting synchronization, as no good LDAP account was found",
            ],
            marks=pytest.mark.envvar(
                {
                    "DISCRIMINATOR_FIELDS": '["sn"]',
                    "DISCRIMINATOR_VALUES": '["__never_gonna_match__"]',
                }
            ),
        ),
        # Discriminator finding original account
        pytest.param(
            True,
            [
                "Found DN",
                "Found DN",
                "Import to MO filtered",
                "Import checks executed",
            ],
            marks=pytest.mark.envvar(
                {
                    "DISCRIMINATOR_FIELDS": '["sn"]',
                    "DISCRIMINATOR_VALUES": "[\"{{ value == 'foo_sn' }}\"]",
                }
            ),
        ),
        # Discriminator finding another account
        pytest.param(
            True,
            [
                "Found DN",
                "Found DN",
                "Found better DN for employee",
                "Import to MO filtered",
                "Import checks executed",
            ],
            marks=pytest.mark.envvar(
                {
                    "DISCRIMINATOR_FIELDS": '["sn"]',
                    "DISCRIMINATOR_VALUES": "[\"{{ value == 'bar_sn' }}\"]",
                }
            ),
        ),
    ],
)
@pytest.mark.envvar(
    {
        "CONVERSION_MAPPING": json.dumps(
            {
                "ldap_to_mo": {
                    "Employee": {
                        "objectClass": "Employee",
                        "_import_to_mo_": "false",
                        "_ldap_attributes_": ["employeeID"],
                        "cpr_number": "{{ldap.employeeID or None}}",
                        "uuid": "{{ employee_uuid or '' }}",
                    }
                },
            }
        )
    }
)
async def test_import_single_user_apply_discriminator(
    ldap_connection: Connection,
    ldap_container_dn: DN,
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
                            "user_key": "Pandamonium",
                            "cpr_number": "0101700001",
                            "given_name": "Chen",
                            "surname": "Stormstout",
                            "nickname_given_name": "Chen",
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
    events = [x["event"] for x in cap_logs if x["log_level"] != "debug"]

    assert (
        events
        == [
            "Importing user",
            "Found DN",
            "Found employee via CPR matching",
            "Attempting to find DNs",
            "Attempting CPR number lookup",
            "Found LDAP(s) object",
            "Found DN(s) using CPR number lookup",
            "Found DNs for MO employee",
        ]
        + log_lines
    )


@pytest.mark.parametrize(
    "extra_account,log_lines",
    [
        # Discriminator not configured
        pytest.param(
            False,
            [
                "Not writing to LDAP as changeset is empty",
            ],
            marks=pytest.mark.envvar({}),
        ),
        # Discriminator rejecting all accounts
        pytest.param(
            True,
            [
                "Found DN",
                "Found DN",
                "Aborting synchronization, as no good LDAP account was found",
            ],
            marks=pytest.mark.envvar(
                {
                    "DISCRIMINATOR_FIELDS": '["sn"]',
                    "DISCRIMINATOR_VALUES": '["__never_gonna_match__"]',
                }
            ),
        ),
        # Discriminator finding original account
        pytest.param(
            True,
            [
                "Found DN",
                "Found DN",
                "Not writing to LDAP as changeset is empty",
            ],
            marks=pytest.mark.envvar(
                {
                    "DISCRIMINATOR_FIELDS": '["sn"]',
                    "DISCRIMINATOR_VALUES": "[\"{{ value == 'foo_sn' }}\"]",
                }
            ),
        ),
        # Discriminator finding another account
        pytest.param(
            True,
            [
                "Found DN",
                "Found DN",
                "Not writing to LDAP as changeset is empty",
            ],
            marks=pytest.mark.envvar(
                {
                    "DISCRIMINATOR_FIELDS": '["sn"]',
                    "DISCRIMINATOR_VALUES": "[\"{{ value == 'bar_sn' }}\"]",
                }
            ),
        ),
    ],
)
async def test_listen_to_changes_in_employees(
    ldap_connection: Connection,
    ldap_container_dn: DN,
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
                            "user_key": "Pandamonium",
                            "cpr_number": "0101700001",
                            "given_name": "Chen",
                            "surname": "Stormstout",
                            "nickname_given_name": "Chen",
                            "nickname_surname": "Brewmaster",
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(employee_uuid)
    events = [x["event"] for x in cap_logs if x["log_level"] != "debug"]

    assert (
        events
        == [
            "Registered change in an employee",
            "Attempting to find DNs",
            "Attempting CPR number lookup",
            "Found LDAP(s) object",
            "Found DN(s) using CPR number lookup",
            "Found DNs for MO employee",
            "Found DNs for user",
        ]
        + log_lines
    )


@pytest.mark.parametrize(
    "fields,dn_map,template,expected",
    [
        # Single field
        # Check no template matches
        (["sn"], {"CN=foo": {}, "CN=bar": {}}, "{{ False }}", None),
        (["sn"], {"CN=foo": {}, "CN=bar": {}}, "{{ 'PleaseHelpMe' }}", None),
        # Check dn is specific value
        (["sn"], {"CN=foo": {}, "CN=bar": {}}, "{{ dn == 'CN=foo' }}", "CN=foo"),
        (["sn"], {"CN=foo": {}, "CN=bar": {}}, "{{ dn == 'CN=bar' }}", "CN=bar"),
        # Check SN value
        (
            ["sn"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ value == 'foo' }}",
            "CN=foo",
        ),
        (
            ["sn"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ value == 'bar' }}",
            "CN=bar",
        ),
        (
            ["sn"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ sn == 'foo' }}",
            "CN=foo",
        ),
        (
            ["sn"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ sn == 'bar' }}",
            "CN=bar",
        ),
        # Check SN substring
        (
            ["sn"],
            {"CN=foo": {"sn": "something foo maybe"}, "CN=bar": {"sn": "bar"}},
            "{{ 'foo' in value }}",
            "CN=foo",
        ),
        (
            ["sn"],
            {"CN=foo": {"sn": "something foo maybe"}, "CN=bar": {"sn": "bar"}},
            "{{ 'foo' in sn }}",
            "CN=foo",
        ),
        # Check SN even
        (
            ["sn"],
            {"CN=foo": {"sn": "1"}, "CN=bar": {"sn": "3"}, "CN=baz": {"sn": "0"}},
            "{{ value|int % 2 == 0 }}",
            "CN=baz",
        ),
        (
            ["sn"],
            {"CN=foo": {"sn": "1"}, "CN=bar": {"sn": "3"}, "CN=baz": {"sn": "0"}},
            "{{ sn|int % 2 == 0 }}",
            "CN=baz",
        ),
        # Check default filters and globals, SN is even after removing things
        (
            ["sn"],
            {
                "CN=foo": {"sn": "{{1a1}}"},
                "CN=bar": {"sn": "{3b}"},
                "CN=baz": {"sn": "{0c2}"},
            },
            "{{ sn|strip_non_digits|remove_curly_brackets|int % 2 == 0 }}",
            "CN=baz",
        ),
        # Multiple fields
        # Check SN value
        (
            ["sn", "uid"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ value == 'foo' }}",
            # This is `None` as value is not uniquely determined
            None,
        ),
        (
            ["sn", "uid"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ sn == 'foo' }}",
            "CN=foo",
        ),
        (
            ["sn", "uid"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar"}},
            "{{ uid == 'foo' }}",
            # This is `None` as `uid` is unset
            None,
        ),
        (
            ["sn", "uid"],
            {"CN=foo": {"sn": "foo"}, "CN=bar": {"sn": "bar", "uid": "foo"}},
            "{{ uid == 'foo' }}",
            "CN=bar",
        ),
        (
            ["sn", "uid"],
            {
                "CN=foo": {"sn": "foo", "uid": "bar"},
                "CN=bar": {"sn": "bar", "uid": "foo"},
            },
            "{{ uid == 'bar' and sn == 'foo' }}",
            "CN=foo",
        ),
        (
            ["sn", "uid"],
            {
                "CN=foo": {"sn": "foo", "uid": "foo"},
                "CN=bar": {"sn": "bar", "uid": "foo"},
            },
            "{{ uid == sn }}",
            "CN=foo",
        ),
    ],
)
async def test_apply_discriminator_template(
    settings: Settings,
    fields: str,
    dn_map: dict[DN, dict[str, Any]],
    template: str,
    expected: DN | None,
) -> None:
    settings = settings.copy(
        update={
            "discriminator_fields": fields,
            "discriminator_values": [template],
        }
    )
    ldap_connection = AsyncMock()

    async def get_ldap_object(
        ldap_connection: Connection, dn: DN, *args: Any, **kwargs: Any
    ) -> LdapObject:
        return parse_obj_as(LdapObject, {"dn": dn, **dn_map[dn]})

    with patch("mo_ldap_import_export.ldap.get_ldap_object", wraps=get_ldap_object):
        result = await apply_discriminator(
            settings, ldap_connection, set(dn_map.keys())
        )
        assert result == expected


async def test_get_existing_values(sync_tool: SyncTool, context: Context) -> None:
    user_context = context["user_context"]
    username_generator = UserNameGenerator(
        user_context["settings"], user_context["ldap_connection"]
    )

    result = await username_generator.get_existing_values(["sAMAccountName", "cn"])
    assert result == {"cn": {"foo"}, "sAMAccountName": set()}

    result = await username_generator.get_existing_values(["employeeID"])
    assert result == {"employeeID": {"0101700001"}}


async def test_get_existing_names(sync_tool: SyncTool, context: Context) -> None:
    settings = context["user_context"]["settings"]
    settings = settings.copy(update={"ldap_dialect": "Standard"})
    context["user_context"]["settings"] = settings

    user_context = context["user_context"]
    username_generator = UserNameGenerator(
        user_context["settings"], user_context["ldap_connection"]
    )

    result = await username_generator._get_existing_common_names()
    assert result == {"foo"}


async def test_load_ldap_OUs(
    ldap_connection: Connection,
    ldap_container_dn: DN,
    context: Context,
) -> None:
    group_dn1 = f"OU=Users,{ldap_container_dn}"
    ldap_connection.strategy.add_entry(
        group_dn1,
        {
            "objectClass": "organizationalUnit",
            "ou": "Users",
            "revision": 1,
            "entryUUID": "{" + str(uuid4()) + "}",
        },
    )
    group_dn2 = f"OU=Groups,{ldap_container_dn}"
    ldap_connection.strategy.add_entry(
        group_dn2,
        {
            "objectClass": "organizationalUnit",
            "ou": "Groups",
            "revision": 1,
            "entryUUID": "{" + str(uuid4()) + "}",
        },
    )

    user_dn = f"CN=Nick Janssen,{group_dn1}"
    ldap_connection.strategy.add_entry(
        user_dn,
        {
            "objectClass": "inetOrgPerson",
            "userPassword": str(uuid4()),
            "sn": "Janssen",
            "revision": 1,
            "entryUUID": "{" + str(uuid4()) + "}",
            "employeeID": "0101700001",
        },
    )

    settings = context["user_context"]["settings"]
    output = await load_ldap_OUs(settings, ldap_connection, ldap_container_dn)

    ou1 = extract_ou_from_dn(group_dn1)
    ou2 = extract_ou_from_dn(group_dn2)
    assert output == {
        ou1: {"empty": True, "dn": group_dn1},
        ou2: {"empty": True, "dn": group_dn2},
    }
