# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import json
import time
from functools import partial
from itertools import combinations
from random import randint
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from fastramqpi.ramqp.utils import RequeueMessage
from freezegun import freeze_time
from more_itertools import one
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.environments import construct_environment
from mo_ldap_import_export.exceptions import DNNotFound
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.main import handle_org_unit
from mo_ldap_import_export.moapi import Verb
from mo_ldap_import_export.moapi import get_primary_engagement
from mo_ldap_import_export.models import Address
from mo_ldap_import_export.models import Employee
from mo_ldap_import_export.models import Engagement
from mo_ldap_import_export.models import JobTitleFromADToMO
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import EmployeeUUID
from mo_ldap_import_export.types import OrgUnitUUID
from tests.graphql_mocker import GraphQLMocker


@pytest.fixture
def context(
    dataloader: AsyncMock,
    converter: MagicMock,
    export_checks: AsyncMock,
    import_checks: AsyncMock,
    settings_mock: MagicMock,
) -> Context:
    settings_mock.discriminator_field = None
    settings_mock.discriminator_fields = []
    ldap_connection = AsyncMock()
    context = Context(
        amqpsystem=AsyncMock(),
        user_context={
            "dataloader": dataloader,
            "converter": converter,
            "export_checks": export_checks,
            "import_checks": import_checks,
            "settings": settings_mock,
            "ldap_connection": ldap_connection,
        },
    )
    return context


@pytest.fixture
def sync_tool(context: Context) -> SyncTool:
    user_context = context["user_context"]
    sync_tool = SyncTool(**user_context)
    return sync_tool


@pytest.fixture
def fake_dn() -> DN:
    return DN("CN=foo")


@pytest.fixture
def fake_find_mo_employee_dn(sync_tool: SyncTool, fake_dn: DN) -> None:
    sync_tool.dataloader.find_mo_employee_dn.return_value = {fake_dn}  # type: ignore


async def test_listen_to_changes_in_employees_no_dn(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    employee_uuid = uuid4()
    dataloader.find_mo_employee_dn.return_value = set()
    dataloader.make_mo_employee_dn.side_effect = DNNotFound("Not found")
    sync_tool.dataloader._find_best_dn = partial(  # type: ignore
        DataLoader._find_best_dn,
        sync_tool.dataloader,  # type: ignore
    )

    with capture_logs() as cap_logs:
        with pytest.raises(RequeueMessage):
            await sync_tool.listen_to_changes_in_employees(employee_uuid)

        messages = [w["event"] for w in cap_logs]
        assert messages == [
            "Registered change in an employee",
            "create_user_trees not configured, allowing create",
            "Unable to generate DN",
        ]


async def test_format_converted_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.get_mo_attributes.return_value = ["user_key", "job_function"]

    employee_uuid = uuid4()

    mo_engagement = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="mo",
        validity={"start": "2021-01-01T00:00:00"},
    )

    ldap_engagement = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="ldap",
        validity={"start": "2021-01-01T00:00:00"},
        # Templated to match MO engagement
        uuid=mo_engagement.uuid,
    )

    dataloader.moapi.load_mo_engagement.return_value = mo_engagement

    operations = await sync_tool.format_converted_objects(
        [ldap_engagement], json_key="Engagement"
    )
    desired_engagement, verb = one(operations)
    assert verb == Verb.EDIT
    assert isinstance(desired_engagement, Engagement)
    assert desired_engagement.user_key == ldap_engagement.user_key


async def test_format_converted_engagement_objects_unmatched(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.get_mo_attributes.return_value = ["user_key", "job_function"]

    employee_uuid = uuid4()

    ldap_engagement = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="ldap",
        validity={"start": "2021-01-01T00:00:00"},
        # Unmatched
        uuid=uuid4(),
    )

    dataloader.moapi.load_mo_engagement.return_value = None

    operations = await sync_tool.format_converted_objects(
        [ldap_engagement], json_key="Engagement"
    )
    desired_engagement, verb = one(operations)
    assert verb == Verb.CREATE
    assert isinstance(desired_engagement, Engagement)
    assert desired_engagement.user_key == ldap_engagement.user_key


async def test_format_converted_employee_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.import_mo_object_class.return_value = Employee

    employee1 = Employee(cpr_number="1212121234", given_name="Foo1", surname="Bar1")
    employee2 = Employee(cpr_number="1212121235", given_name="Foo2", surname="Bar2")

    converted_objects = [employee1, employee2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects, "Employee"
    )

    assert formatted_objects[0][0] == employee1
    assert formatted_objects[1][0] == employee2


@pytest.mark.usefixtures("minimal_valid_settings")
async def test_import_single_object_no_employee_no_sync(
    sync_tool: SyncTool, monkeypatch: pytest.MonkeyPatch
) -> None:
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
            }
        ),
    )

    # Note that converter.settings and dataloader.settings are still mocked
    sync_tool.settings = Settings()
    # Ignore typing since it is actually a mock
    sync_tool.dataloader.find_mo_employee_uuid.return_value = None  # type: ignore

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user("CN=foo")

    messages = [w["event"] for w in cap_logs]
    assert messages == [
        "Generating DN",
        "Importing user",
        "Employee not found in MO, and not configured to create it",
    ]


@pytest.mark.usefixtures("fake_find_mo_employee_dn", "minimal_valid_settings")
async def test_import_single_object_from_LDAP_but_import_equals_false(
    sync_tool: SyncTool, monkeypatch: pytest.MonkeyPatch
) -> None:
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
            }
        ),
    )

    # Note that converter.settings and dataloader.settings are still mocked
    sync_tool.settings = Settings()

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user("CN=foo")
        messages = [w["event"] for w in cap_logs if w["log_level"] == "info"]
        assert "Import to MO filtered" in messages
        assert "Loading object" not in messages


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_forces_json_key_ordering(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    """
    Verify that `import_single_object` visits each "JSON key" in a specific order.
    `Employee` keys must be visited first, then `Engagement` keys, and finally all other
    keys.
    """
    # Arrange: inject a list of JSON keys that have the wrong order
    sync_tool.format_converted_objects = AsyncMock()  # type: ignore
    sync_tool.format_converted_objects.return_value = []

    sync_tool.settings.conversion_mapping.ldap_to_mo.keys.return_value = {  # type: ignore
        "Employee",
        "Engagement",
        "Address",
    }
    converter.from_ldap.return_value = [MagicMock()]  # list of (at least) one item
    # Act: run the method and collect logs
    with (
        capture_logs() as cap_logs,
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user("CN=foo")
        # Assert: verify that we process JSON keys in the expected order, regardless of
        # the original ordering.
        logged_json_keys: list[str] = [
            m["json_key"]
            for m in cap_logs
            if m.get("json_key") and "Loaded object" in m["event"]
        ]
        assert logged_json_keys == ["Employee", "Engagement", "Address"]


async def test_wait_for_import_to_finish(sync_tool: SyncTool):
    wait_for_import_to_finish = partial(sync_tool.wait_for_import_to_finish)

    @wait_for_import_to_finish
    async def decorated_func(self, dn):
        await asyncio.sleep(0.2)
        return

    async def regular_func(self, dn):
        await asyncio.sleep(0.2)
        return

    dn = "CN=foo"
    different_dn = "CN=bar"

    # Normally this would execute in 0.2 seconds + overhead
    t1 = time.time()
    await asyncio.gather(
        regular_func(sync_tool, dn),
        regular_func(sync_tool, dn),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.2
    assert elapsed_time < 0.3

    # But the decorator will make the second call wait for the first one to complete
    t1 = time.time()
    await asyncio.gather(
        decorated_func(sync_tool, dn),
        decorated_func(sync_tool, dn),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.4
    assert elapsed_time < 0.5

    # But only if payload.uuid is the same in both calls
    t1 = time.time()
    await asyncio.gather(
        decorated_func(sync_tool, dn),
        decorated_func(sync_tool, different_dn),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.2
    assert elapsed_time < 0.3


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_jobtitlefromadtomo_objects(
    context: Context,
    converter: MagicMock,
    sync_tool: SyncTool,
    fake_dn: DN,
) -> None:
    converter.find_mo_object_class.return_value = (
        "mo_ldap_import_export.customer_specific.JobTitleFromADToMO"
    )
    converter.import_mo_object_class.return_value = JobTitleFromADToMO
    converter.get_mo_attributes.return_value = ["user", "uuid", "job_function"]
    sync_tool.settings.conversion_mapping.ldap_to_mo.keys.return_value = {  # type: ignore
        "Custom"
    }

    user_uuid = uuid4()
    converted_object = JobTitleFromADToMO(
        user=user_uuid,
        job_function=uuid4(),
    )
    converted_objects = [converted_object]
    formatted_objects = [
        (converted_object, Verb.CREATE) for converted_object in converted_objects
    ]
    converter.from_ldap.return_value = converted_objects

    with (
        patch(
            "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
            return_value=formatted_objects,
        ),
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user(fake_dn)

    graphql_client_mock: AsyncMock = sync_tool.dataloader.moapi.graphql_client  # type: ignore
    graphql_client_mock.read_engagements_by_employee_uuid.assert_called_once_with(
        user_uuid
    )


async def test_publish_engagements_for_org_unit(dataloader: AsyncMock) -> None:
    amqpsystem = AsyncMock()
    amqpsystem.exchange_name = "my-unique-exchange-name"
    uuid = OrgUnitUUID(uuid4())
    await handle_org_unit(uuid, dataloader.graphql_client, amqpsystem)
    dataloader.graphql_client.org_unit_engagements_refresh.assert_called_with(
        amqpsystem.exchange_name, uuid
    )


async def test_perform_import_checks_noop(sync_tool: SyncTool) -> None:
    """Test that perform_import_checks returns True when nothing is checked."""
    sync_tool.settings.check_holstebro_ou_issue_57426 = False  # type: ignore
    result = await sync_tool.perform_import_checks("CN=foo", "Employee")
    assert result is True


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_holstebro_import_checks(sync_tool: SyncTool, fake_dn: DN) -> None:
    with (
        patch(
            "mo_ldap_import_export.import_export.SyncTool.perform_import_checks",
            return_value=False,
        ),
        capture_logs() as cap_logs,
    ):
        await sync_tool.import_single_user(fake_dn)
        assert "Import checks executed" in str(cap_logs)


async def test_import_single_user_entity(sync_tool: SyncTool) -> None:
    sync_tool.converter.from_ldap.return_value = []  # type: ignore

    json_key = "Engagement"
    dn = "CN=foo"
    employee_uuid = uuid4()
    with (
        capture_logs() as cap_logs,
        patch("mo_ldap_import_export.import_export.get_ldap_object"),
    ):
        await sync_tool.import_single_user_entity(json_key, dn, employee_uuid)

        assert "No converted objects" in str(cap_logs)


engagement_uuid1 = uuid4()
engagement_uuid2 = uuid4()
engagement_uuid3 = uuid4()

waiting_for_primary = "Waiting for primary engagement to be decided"
waiting_for_multiple = "Waiting for multiple primary engagements to be resolved"

past = {"from": "1970-01-01T00:00:00Z", "to": "1980-01-01T00:00:00Z"}
current = {"from": "1970-01-01T00:00:00Z", "to": None}
future = {"from": "9970-01-01T00:00:00Z", "to": None}


def generate_random_validity() -> dict[str, str | None]:
    # TODO: Actually generate proper random dates?
    # TODO: Generate None in end date?
    start_year = randint(1000, 9999)
    end_year = randint(start_year, 9999)
    return {
        "from": f"{start_year}-01-01T00:00:00Z",
        "to": f"{end_year}-01-02T00:00:00Z",
    }


def construct_validity(is_primary: bool, validity: Any, uuid: UUID) -> dict[str, Any]:
    return {"is_primary": is_primary, "uuid": uuid, "validity": validity}


def generate_object():
    # TODO: Replace this with hypothesis?
    num_validities = randint(1, 5)
    return {
        "validities": [
            construct_validity(False, generate_random_validity(), engagement_uuid1)
            for _ in range(num_validities)
        ]
    }


@pytest.mark.parametrize(
    "objects,expected",
    [
        # No objects, no validities
        ([], None),
    ]
    + [
        # Any number of objects with any number of validities, but no primary
        (
            [generate_object() for _ in range(num_objects)],
            waiting_for_primary,
        )
        for num_objects in range(1, 5)
    ]
    + [
        # One primary, any time
        (
            [{"validities": [construct_validity(True, validity, engagement_uuid1)]}],
            engagement_uuid1,
        )
        for validity in [past, current, future]
    ]
    + [
        # Two validities, non primary and primary, any time
        # Any combination of times should be okay here
        (
            [
                {
                    "validities": [
                        construct_validity(False, val1, engagement_uuid1),
                        construct_validity(True, val2, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        )
        for val1, val2 in combinations([past, current, future], 2)
    ]
    + [
        # Two objects with one validity each, non primary and primary, any time
        # Any combination of times should be okay here
        (
            [
                {"validities": [construct_validity(False, val1, engagement_uuid1)]},
                {"validities": [construct_validity(True, val2, engagement_uuid2)]},
            ],
            engagement_uuid2,
        )
        for val1, val2 in combinations([past, current, future], 2)
    ]
    + [
        # Two validities, both primary, both current
        (
            [
                {
                    "validities": [
                        construct_validity(True, current, engagement_uuid1),
                        construct_validity(True, current, engagement_uuid1),
                    ]
                }
            ],
            waiting_for_multiple,
        ),
        # Two object with one validity each, both primary, both current
        (
            [
                {
                    "validities": [
                        construct_validity(True, current, engagement_uuid1),
                    ]
                },
                {"validities": [construct_validity(True, current, engagement_uuid1)]},
            ],
            waiting_for_multiple,
        ),
        # Two validities both primary, both past
        # TODO: This should probably fail like the above
        (
            [
                {
                    "validities": [
                        construct_validity(True, past, engagement_uuid1),
                        construct_validity(True, past, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        ),
        # Two object with one validity each, both primary, both past
        # TODO: This should probably fail like the above
        # NOTE: Whichever comes first wins, is this well-defined in MO?
        (
            [
                {
                    "validities": [
                        construct_validity(True, past, engagement_uuid1),
                    ]
                },
                {"validities": [construct_validity(True, past, engagement_uuid2)]},
            ],
            engagement_uuid1,
        ),
        # Two validities both primary, both future
        # TODO: This should probably fail like the above
        (
            [
                {
                    "validities": [
                        construct_validity(True, future, engagement_uuid1),
                        construct_validity(True, future, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        ),
        # Two object with one validity each, both primary, both future
        # TODO: This should probably fail like the above
        # NOTE: Whichever comes first wins, is this well-defined in MO?
        (
            [
                {
                    "validities": [
                        construct_validity(True, future, engagement_uuid2),
                    ]
                },
                {"validities": [construct_validity(True, future, engagement_uuid1)]},
            ],
            engagement_uuid2,
        ),
    ]
    + [
        # Two validities both primary, temporally spread
        (
            [
                {
                    "validities": [
                        construct_validity(True, val1, engagement_uuid1),
                        construct_validity(True, val2, engagement_uuid1),
                    ]
                }
            ],
            engagement_uuid1,
        )
        for val1, val2 in [(past, current), (past, future), (current, future)]
    ]
    + [
        # Two object with one validity each, both primary, temporally spread
        (
            [
                {"validities": [construct_validity(True, val1, engagement_uuid1)]},
                {"validities": [construct_validity(True, val2, engagement_uuid2)]},
            ],
            expected,
        )
        for val1, val2, expected in [
            (past, current, engagement_uuid2),
            (past, future, engagement_uuid2),
            (current, future, engagement_uuid1),
        ]
    ]
    + [
        # Three engagements all primary, all temporally spread
        (
            [
                {
                    "validities": [
                        construct_validity(True, past, engagement_uuid1),
                        construct_validity(True, current, engagement_uuid2),
                        construct_validity(True, future, engagement_uuid3),
                    ]
                }
            ],
            engagement_uuid2,
        ),
        # Three objects with one validity each, all primary, all temporally spread
        (
            [
                {"validities": [construct_validity(True, past, engagement_uuid1)]},
                {
                    "validities": [
                        construct_validity(True, current, engagement_uuid2),
                    ]
                },
                {"validities": [construct_validity(True, future, engagement_uuid3)]},
            ],
            engagement_uuid2,
        ),
    ],
)
async def test_get_primary_engagement(
    graphql_mock: GraphQLMocker,
    objects: list[dict[str, Any]],
    expected: UUID | str | None,
) -> None:
    graphql_client = GraphQLClient("http://example.com/graphql")

    employee_uuid = EmployeeUUID(uuid4())

    route = graphql_mock.query("read_engagements_is_primary")
    route.result = {"engagements": {"objects": objects}}

    if isinstance(expected, str):
        with pytest.raises(RequeueMessage) as exc_info:
            await get_primary_engagement(graphql_client, employee_uuid)
        assert expected in str(exc_info.value)
    else:
        result = await get_primary_engagement(graphql_client, employee_uuid)
        assert result == expected

    assert route.called


async def test_find_best_dn(sync_tool: SyncTool) -> None:
    dn = "CN=foo"
    sync_tool.dataloader.find_mo_employee_dn.return_value = set()  # type: ignore
    sync_tool.dataloader.make_mo_employee_dn.return_value = dn  # type: ignore
    sync_tool.dataloader._find_best_dn = partial(  # type: ignore
        DataLoader._find_best_dn, sync_tool.dataloader
    )

    uuid = EmployeeUUID(uuid4())
    result, create = await sync_tool.dataloader._find_best_dn(uuid)
    assert result == dn
    assert create is True


@freeze_time("2022-08-10T12:34:56")
@pytest.mark.parametrize(
    "template, expected",
    (
        # No result call, gives decode error
        ("", "Expecting value"),
        # Empty dict in result call, works as expected
        ("{{ {} }}", {}),
        # Empty dict in result call, works as expected
        ("{{ dict() }}", {}),
        # Empty dict in result call with tojson, works as expected
        ("{{ dict()|tojson }}", {}),
        # Actual dict in result call, but single quotes, gives decode error
        ("{{ {'a': 'b'} }}", "Expecting property name enclosed in double quotes"),
        # Actual dict in result call, with double quotes, works as expected
        ('{{ {"a": "b"} }}', "Expecting property name enclosed in double quotes"),
        # Actual dict in result call, but single quotes with tojson, works as expected
        ("{{ {'a': 'b'}|tojson }}", {"a": ["b"]}),
        # Multiple result calls, give value error
        (
            '{{ {"a": "b"} }} {{ {"c": "d"} }}',
            "Expecting property name enclosed in double quotes",
        ),
        # Templates can use context
        ('{{ {"a": dn} }}', "Expecting property name enclosed in double quotes"),
        ('{{ {"a": dn}|tojson }}', {"a": ["CN=foo"]}),
        ('{{ {"b": uuid} }}', "Expecting property name enclosed in double quotes"),
        ("{{ {'b': uuid}|tojson }}", "Object of type UUID is not JSON serializable"),
        (
            "{{ {'b': uuid|string}|tojson }}",
            {"b": ["fa15edad-da1e-c0de-babe-c1a551f1ab1e"]},
        ),
        # Templates can use set operations
        ("{% set a = 'hej' %} {{ {'a': a}|tojson }}", {"a": ["hej"]}),
        # Templates can filters
        (
            "{% set a = 'hej123'|strip_non_digits %} {{ {'a': a}|tojson }}",
            {"a": ["123"]},
        ),
        # Templates can use globals (and filters)
        (
            "{% set a = now()|mo_datestring %} {{ {'a': a}|tojson }}",
            {"a": ["2022-08-10T00:00:00"]},
        ),
        # Generating raw json outside of tojson
        ('{"key": "value"}', {"key": ["value"]}),
        ('{"key": "{{ dn }}"}', {"key": ["CN=foo"]}),
        # Accessing undefined variable
        (
            '{"key": "{{ foobar }}"}',
            "Undefined variable 'foobar' with object missing (hint: None)",
        ),
    ),
)
async def test_render_ldap2mo(
    sync_tool: SyncTool, template: str, expected: dict | str
) -> None:
    sync_tool.settings.conversion_mapping.mo2ldap = template  # type: ignore
    sync_tool.converter.environment = construct_environment(
        sync_tool.settings, sync_tool.dataloader
    )
    uuid = EmployeeUUID(UUID("fa15edad-da1e-c0de-babe-c1a551f1ab1e"))
    if isinstance(expected, str):
        with pytest.raises(Exception) as exc_info:
            await sync_tool.render_ldap2mo(uuid, "CN=foo")
        assert expected in str(exc_info.value)
    else:
        result = await sync_tool.render_ldap2mo(uuid, "CN=foo")
        assert result == expected


async def test_noop_listen_to_changes(sync_tool: SyncTool) -> None:
    sync_tool.settings.conversion_mapping.mo2ldap = None  # type: ignore

    with capture_logs() as cap_logs:
        result = await sync_tool.listen_to_changes_in_employees(uuid4())
    assert result == {}

    messages = [w["event"] for w in cap_logs]
    assert messages == [
        "Registered change in an employee",
        "listen_to_changes_in_employees called without mapping",
    ]


async def test_noop_import_single_user(sync_tool: SyncTool) -> None:
    sync_tool.settings.conversion_mapping.ldap_to_mo = None  # type: ignore

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user(uuid4())

    messages = [w["event"] for w in cap_logs]
    assert messages == [
        "Generating DN",
        "Importing user",
        "import_single_user called without mapping",
    ]
