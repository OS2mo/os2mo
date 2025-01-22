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
from more_itertools import first
from more_itertools import last
from more_itertools import one
from structlog.testing import capture_logs

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.environments import construct_environment
from mo_ldap_import_export.exceptions import DNNotFound
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.main import handle_org_unit
from mo_ldap_import_export.moapi import Verb
from mo_ldap_import_export.moapi import get_primary_engagement
from mo_ldap_import_export.models import Address
from mo_ldap_import_export.models import Employee
from mo_ldap_import_export.models import Engagement
from mo_ldap_import_export.models import ITUser
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

    with capture_logs() as cap_logs:
        with pytest.raises(RequeueMessage):
            await sync_tool.listen_to_changes_in_employees(employee_uuid)

        messages = [w["event"] for w in cap_logs]
        assert messages == [
            "Registered change in an employee",
            "Unable to generate DN",
        ]


async def test_format_converted_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Engagement": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    employee_uuid = uuid4()

    engagement1 = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2021-01-01T00:00:00"},
    )

    engagement2 = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="foo",
        validity={"start": "2021-01-01T00:00:00"},
    )

    engagement_in_mo = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2021-01-01T00:00:00"},
    )

    dataloader.moapi.load_mo_employee_engagements.return_value = [
        engagement_in_mo,
    ]

    json_key = "Engagement"

    converted_objects = [engagement1, engagement2]

    operations = await sync_tool.format_converted_objects(
        converted_objects,
        json_key,
    )
    assert len(operations) == 2
    (e1, _), (e2, _) = operations
    assert isinstance(e1, Engagement)
    assert isinstance(e2, Engagement)
    assert e2.uuid == engagement_in_mo.uuid
    assert e2.user_key == engagement1.user_key
    assert e1 == engagement2


async def test_format_converted_engagement_duplicate(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.mapping = {"ldap_to_mo": {"Engagement": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    employee_uuid = uuid4()

    engagement = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="duplicate_key",
        validity={"start": "2021-01-01T00:00:00"},
    )

    engagement1_in_mo = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="duplicate_key",
        validity={"start": "2021-01-01T00:00:00"},
    )
    engagement2_in_mo = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="duplicate_key",
        validity={"start": "2021-01-01T00:00:00"},
    )

    dataloader.moapi.load_mo_employee_engagements.return_value = [
        engagement1_in_mo,
        engagement2_in_mo,
    ]

    json_key = "Engagement"

    converted_objects = [engagement]
    with pytest.raises(RequeueMessage) as exc_info:
        await sync_tool.format_converted_objects(converted_objects, json_key)
    assert "Bad mapping: Multiple MO objects" in str(exc_info.value)


async def test_format_converted_multiple_primary_engagements(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.import_mo_object_class.return_value = Engagement

    employee_uuid = uuid4()

    engagement1 = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2020-01-01T00:00:00"},
    )

    engagement2 = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2020-01-01T00:00:00"},
    )

    dataloader.moapi.load_mo_employee_engagements.return_value = [
        engagement1,
        engagement2,
    ]

    dataloader.moapi.is_primaries.return_value = [True, True]

    converted_objects = [engagement1, engagement2]

    with pytest.raises(RequeueMessage) as exc_info:
        await sync_tool.format_converted_objects(
            converted_objects,
            json_key="Engagement",
        )
    assert "Waiting for multiple primary engagements to be resolved" in str(
        exc_info.value
    )


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


async def test_format_converted_employee_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Address": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    person = uuid4()
    address_type = uuid4()
    address1 = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        person=person,
    )
    address2 = Address(
        value="bar",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        person=person,
    )
    address1_in_mo = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        person=person,
    )

    converted_objects = [address1, address2]

    dataloader.moapi.load_mo_employee_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[1][0].uuid == address1_in_mo.uuid
    assert formatted_objects[1][0].value == "foo"  # type: ignore

    # Simulate that a matching employee for this address does not exist
    dataloader.moapi.load_mo_employee_addresses.side_effect = (
        NoObjectsReturnedException("f")
    )
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "Address")


async def test_format_converted_org_unit_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Address": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    org_unit = uuid4()
    address_type = uuid4()
    address1 = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        org_unit=org_unit,
    )
    address2 = Address(
        value="bar",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        org_unit=org_unit,
    )
    address1_in_mo = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        org_unit=org_unit,
    )

    converted_objects = [address1, address2]

    dataloader.moapi.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[1][0].uuid == address1_in_mo.uuid
    assert formatted_objects[1][0].value == "foo"  # type: ignore

    # Simulate that a matching org unit for this address does not exist
    dataloader.moapi.load_mo_org_unit_addresses.side_effect = (
        NoObjectsReturnedException("f")
    )
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "Address")


async def test_format_converted_org_unit_address_objects_identical_to_mo(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Address": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    org_unit = uuid4()
    address_type = uuid4()
    address1 = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        org_unit=org_unit,
    )
    address2 = Address(
        value="bar",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        org_unit=org_unit,
    )

    # This one is identical to the one which we are trying to upload
    address1_in_mo = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
        org_unit=org_unit,
    )

    converted_objects = [address1, address2]

    dataloader.moapi.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    operations = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )
    assert len(operations) == 2
    formatted_objects = [obj for obj, _ in operations]

    assert last(formatted_objects).value == "foo"  # type: ignore
    assert first(formatted_objects).value == "bar"  # type: ignore


async def test_format_converted_address_objects_without_person_or_org_unit(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    # These addresses have neither an org unit uuid or person uuid. we cannot convert
    # them
    address_type = uuid4()
    address1 = Address(
        value="foo",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
    )
    address2 = Address(
        value="bar",
        address_type=address_type,
        validity={"start": "2021-01-01T00:00:00"},
    )

    converted_objects = [address1, address2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert len(formatted_objects) == 0


async def test_format_converted_it_user_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"ITUser": {"_mapper_": None}}}

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "ITUser"
    converter.import_mo_object_class.return_value = ITUser

    it_user_in_mo = ITUser(
        user_key="Username1",
        itsystem=uuid4(),
        person=uuid4(),
        validity={"start": "2021-01-01T00:00:00"},
    )

    dataloader.moapi.load_mo_employee_it_users.return_value = [it_user_in_mo]

    person_uuid = uuid4()
    it_system_uuid = uuid4()

    it_user1 = ITUser(
        user_key="Username1",
        itsystem=it_system_uuid,
        person=person_uuid,
        validity={"start": "2021-01-01T00:00:00"},
    )
    it_user2 = ITUser(
        user_key="Username2",
        itsystem=it_system_uuid,
        person=person_uuid,
        validity={"start": "2021-01-01T00:00:00"},
    )

    converted_objects = [it_user1, it_user2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "ITUser",
    )

    assert len(formatted_objects) == 2  # was 1
    formatted_user_keys = {
        obj.user_key for obj, _ in formatted_objects if isinstance(obj, ITUser)
    }
    # assert "Username1" not in formatted_user_keys
    assert "Username1" in formatted_user_keys
    assert "Username2" in formatted_user_keys

    # Simulate that a matching employee for this it user does not exist
    dataloader.moapi.load_mo_employee_it_users.side_effect = NoObjectsReturnedException(
        "f"
    )
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "ITUser")


async def test_format_converted_primary_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.mapping = {"ldap_to_mo": {"Engagement": {"_mapper_": None}}}

    employee_uuid = uuid4()
    primary_uuid = uuid4()
    engagement1_in_mo_uuid = uuid4()
    engagement2_in_mo_uuid = uuid4()

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    async def is_primaries(uuids):
        return [uuid == engagement1_in_mo_uuid for uuid in uuids]

    dataloader.moapi.is_primaries = is_primaries

    engagement1 = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2020-01-01T00:00:00"},
    )

    engagement1_in_mo = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2021-01-01T00:00:00"},
        primary=primary_uuid,
        uuid=engagement1_in_mo_uuid,
    )

    # Engagement with the same user key. We should not update this one because it is
    # not primary.
    engagement2_in_mo = Engagement(
        org_unit=uuid4(),
        person=employee_uuid,
        job_function=uuid4(),
        engagement_type=uuid4(),
        user_key="123",
        validity={"start": "2021-01-01T00:00:00"},
        primary=None,
        uuid=engagement2_in_mo_uuid,
    )

    dataloader.moapi.load_mo_employee_engagements.return_value = [
        engagement1_in_mo,
        engagement2_in_mo,
    ]

    json_key = "Engagement"

    converted_objects = [engagement1]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        json_key,
    )

    assert len(formatted_objects) == 1
    obj, _ = one(formatted_objects)
    assert isinstance(obj, Engagement)
    assert obj.primary is not None  # type: ignore
    assert obj.user_key == "123"

    # Simulate that a matching employee for this engagement does not exist
    dataloader.moapi.load_mo_employee_engagements.side_effect = (
        NoObjectsReturnedException("f")
    )
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, json_key)


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
                        "objectClass": "ramodels.mo.employee.Employee",
                        "_import_to_mo_": "false",
                        "_ldap_attributes_": ["employeeID"],
                        "cpr_number": "{{ldap.employeeID or None}}",
                        "uuid": "{{ employee_uuid or '' }}",
                    }
                },
                "username_generator": {"objectClass": "UserNameGenerator"},
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
                        "objectClass": "ramodels.mo.employee.Employee",
                        "_import_to_mo_": "false",
                        "_ldap_attributes_": ["employeeID"],
                        "cpr_number": "{{ldap.employeeID or None}}",
                        "uuid": "{{ employee_uuid or '' }}",
                    }
                },
                "username_generator": {"objectClass": "UserNameGenerator"},
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

    uuid = EmployeeUUID(uuid4())
    result, create = await sync_tool._find_best_dn(uuid)
    assert result == dn
    assert create is True


async def test_find_best_dn_no_create(sync_tool: SyncTool) -> None:
    sync_tool.dataloader.find_mo_employee_dn.return_value = set()  # type: ignore
    sync_tool.settings.add_objects_to_ldap = False  # type: ignore

    uuid = EmployeeUUID(uuid4())
    with capture_logs() as cap_logs:
        result, create = await sync_tool._find_best_dn(uuid)
    assert result is None
    assert create is True

    assert cap_logs == [
        {
            "event": "Aborting synchronization, as no LDAP account was found and we are not configured to create",
            "log_level": "info",
            "uuid": uuid,
        },
    ]


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
