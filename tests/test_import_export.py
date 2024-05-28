# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
import copy
import datetime
import time
from functools import partial
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from fastramqpi.ramqp.mo import MORoutingKey
from fastramqpi.ramqp.utils import RequeueMessage
from httpx import HTTPStatusError
from more_itertools import first
from more_itertools import last
from ramodels.mo.details.address import Address
from ramodels.mo.details.engagement import Engagement
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
from structlog.testing import capture_logs

from mo_ldap_import_export.customer_specific import JobTitleFromADToMO
from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.dataloaders import Verb
from mo_ldap_import_export.depends import GraphQLClient
from mo_ldap_import_export.exceptions import DNNotFound
from mo_ldap_import_export.exceptions import IgnoreChanges
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.import_export import IgnoreMe
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import OrgUnitUUID
from tests.graphql_mocker import GraphQLMocker


@pytest.fixture
def context(
    dataloader: AsyncMock,
    converter: MagicMock,
    export_checks: AsyncMock,
    import_checks: AsyncMock,
    settings: MagicMock,
    amqpsystem: AsyncMock,
) -> Context:
    settings.discriminator_field = None
    context = Context(
        {
            "amqpsystem": amqpsystem,
            "user_context": {
                "dataloader": dataloader,
                "converter": converter,
                "export_checks": export_checks,
                "import_checks": import_checks,
                "settings": settings,
            },
        }
    )
    return context


@pytest.fixture
def sync_tool(context: Context) -> SyncTool:
    sync_tool = SyncTool(context)
    return sync_tool


@pytest.fixture
def fake_dn() -> DN:
    return DN("CN=foo")


@pytest.fixture
def fake_find_mo_employee_dn(sync_tool: SyncTool, fake_dn: DN) -> None:
    sync_tool.dataloader.find_mo_employee_dn.return_value = {fake_dn}  # type: ignore


async def test_listen_to_changes_in_org_units(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    org_unit_info = {uuid4(): {"name": "Magenta Aps"}}

    dataloader.load_mo_org_units.return_value = org_unit_info

    await sync_tool.refresh_org_unit_info_cache()
    assert converter.org_unit_info == org_unit_info


async def test_listen_to_change_in_org_unit_address(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    converter: MagicMock,
    sync_tool: SyncTool,
):
    mo_routing_key: MORoutingKey = "address"

    address = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")
    employee1 = Employee(cpr_no="0101011234")
    employee2 = Employee(cpr_no="0101011235")

    load_mo_address = AsyncMock()
    load_mo_employees_in_org_unit = AsyncMock()
    load_mo_org_unit_addresses = AsyncMock()
    modify_ldap_object = AsyncMock()
    modify_ldap_object.return_value = [{"description": "success"}]

    load_mo_address.return_value = address

    # Note: The same employee is linked to this unit twice;
    # The duplicate employee should not be modified twice
    load_mo_employees_in_org_unit.return_value = [employee1, employee1, employee2]
    load_mo_org_unit_addresses.return_value = [address]

    dataloader.modify_ldap_object = modify_ldap_object
    dataloader.load_mo_address = load_mo_address
    dataloader.load_mo_employees_in_org_unit = load_mo_employees_in_org_unit
    dataloader.load_mo_org_unit_addresses = load_mo_org_unit_addresses

    converter.find_ldap_object_class.return_value = "user"

    payload = MagicMock()
    payload.uuid = uuid4()

    # Simulate another employee which is being processed at the exact same time.
    async def employee_in_progress():
        await asyncio.sleep(1)

    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        with capture_logs() as cap_logs:
            await asyncio.gather(
                employee_in_progress(),
                sync_tool.listen_to_changes_in_org_units(
                    payload.uuid,
                    payload.object_uuid,
                    routing_key=mo_routing_key,
                    delete=False,
                    current_objects_only=True,
                ),
            )
            messages = [w for w in cap_logs if w["log_level"] == "info"]

            # Validate that listen_to_changes_in_org_units had to wait for
            # employee_in_progress to finish
            assert "Generating UUID" in str(messages)

    # Assert that an address was uploaded to two ldap objects
    # (even though load_mo_employees_in_org_unit returned three employee objects)
    assert modify_ldap_object.await_count == 2

    dataloader.find_or_make_mo_employee_dn.side_effect = DNNotFound("DN not found")

    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_org_units(
            payload.uuid,
            payload.object_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        last_log_message = messages[-1]["event"]

        assert last_log_message == "DNNotFound Exception"

    dataloader.find_or_make_mo_employee_dn.side_effect = IgnoreChanges("Ignore this")

    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_org_units(
            payload.uuid,
            payload.object_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        last_log_message = messages[-1]["event"]
        assert last_log_message == "IgnoreChanges Exception"


async def test_listen_to_change_in_org_unit_address_not_supported(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    converter: MagicMock,
    sync_tool: SyncTool,
):
    """
    Mapping an organization unit address to non-employee objects is not supported.
    """
    mo_routing_key: MORoutingKey = "address"
    payload = MagicMock()
    payload.uuid = uuid4()

    address = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")

    def find_ldap_object_class(json_key):
        d = {"Employee": "user", "LocationUnit": "address"}
        return d[json_key]

    converter.find_ldap_object_class.side_effect = find_ldap_object_class

    load_mo_address = AsyncMock()
    load_mo_address.return_value = address
    dataloader.load_mo_address = load_mo_address

    converter.org_unit_address_type_info = {
        str(address.address_type.uuid): {"user_key": "LocationUnit"}
    }
    converter.get_org_unit_address_type_user_key = AsyncMock()
    converter.get_org_unit_address_type_user_key.return_value = "LocationUnit"

    with pytest.raises(NotSupportedException):
        await sync_tool.listen_to_changes_in_org_units(
            payload.uuid,
            payload.object_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )


async def test_listen_to_changes_in_employees_person(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}

    # Simulate a created employee
    mo_routing_key: MORoutingKey = "person"
    await sync_tool.listen_to_changes_in_employees(
        # uuid and object uuid are always the same for person
        uuid=employee_uuid,
        object_uuid=employee_uuid,
        routing_key=mo_routing_key,
        delete=False,
        current_objects_only=True,
    )
    assert dataloader.load_mo_employee.called
    assert converter.to_ldap.called
    assert dataloader.modify_ldap_object.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, "Employee", overwrite=True, delete=False
    )


async def test_listen_to_changes_in_employees_address(
    dataloader: AsyncMock,
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    address_type_user_key = "EmailEmployee"

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}
    dataloader.extract_current_or_latest_object = (
        DataLoader.extract_current_or_latest_object
    )

    # Simulate a created address

    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    # Mock MO read
    route = graphql_mock.query("read_filtered_addresses")
    route.result = {
        "addresses": {
            "objects": [
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": test_mo_address.uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                }
            ]
        }
    }

    mo_routing_key = "address"
    await sync_tool.listen_to_changes_in_employees(
        employee_uuid,
        test_mo_address.uuid,
        routing_key=mo_routing_key,
        delete=False,
        current_objects_only=True,
    )
    assert route.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, address_type_user_key, delete=False
    )

    # Test expected behavior when reading multiple addresses of the same type
    route.result = {
        "addresses": {
            "objects": [
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": test_mo_address.uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
                {
                    "validities": [
                        {
                            "address_type": {"user_key": address_type_user_key},
                            "uuid": UUID(int=test_mo_address.uuid.int + 1),
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
            ]
        }
    }
    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(
            employee_uuid,
            test_mo_address.uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )
    assert "Multiple addresses of same type" in [x["event"] for x in cap_logs]

    # Test expected behavior when unable to read address details
    dataloader.load_mo_address.side_effect = NoObjectsReturnedException("BOOM")
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(
            employee_uuid,
            test_mo_address.uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )
    assert "Unable to load mo object" in str(exc.value)


async def test_listen_to_changes_in_employees_ituser(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    ituser_uuid = uuid4()
    it_system_type_name = "AD"

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}
    dataloader.extract_current_or_latest_object = (
        DataLoader.extract_current_or_latest_object
    )

    # Simulate a created IT user

    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    # Mock MO read
    route = graphql_mock.query("read_filtered_itusers")
    route.result = {
        "itusers": {
            "objects": [
                {
                    "validities": [
                        {
                            "itsystem": {"user_key": it_system_type_name},
                            "uuid": ituser_uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                }
            ]
        }
    }

    mo_routing_key = "ituser"
    await sync_tool.listen_to_changes_in_employees(
        employee_uuid,
        ituser_uuid,
        routing_key=mo_routing_key,
        delete=False,
        current_objects_only=True,
    )
    assert route.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, it_system_type_name, delete=False
    )

    # Test expected behavior when reading multiple addresses of the same type
    route.result = {
        "itusers": {
            "objects": [
                {
                    "validities": [
                        {
                            "itsystem": {"user_key": it_system_type_name},
                            "uuid": ituser_uuid,
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
                {
                    "validities": [
                        {
                            "itsystem": {"user_key": it_system_type_name},
                            "uuid": UUID(int=ituser_uuid.int + 1),
                            "validity": {
                                "from": "1970-01-01T00:00:00",
                                "to": None,
                            },
                        }
                    ]
                },
            ]
        }
    }
    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(
            employee_uuid,
            ituser_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )
    assert "Multiple itusers with the same itsystem" in [x["event"] for x in cap_logs]

    # Test expected behavior when unable to read address details
    dataloader.load_mo_it_user.side_effect = NoObjectsReturnedException("BOOM")
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(
            employee_uuid,
            ituser_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )
    assert "Unable to load mo object" in str(exc.value)


async def test_listen_to_changes_in_employees_engagement(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
    graphql_mock: GraphQLMocker,
) -> None:
    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    engagement_uuid = uuid4()

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}
    dataloader.extract_current_or_latest_object = (
        DataLoader.extract_current_or_latest_object
    )
    dataloader.load_mo_engagement = partial(  # partial to seed 'self'
        DataLoader.load_mo_engagement, dataloader
    )

    # Simulate a created engagement
    # Replace the shitty mock with a good mock
    dataloader.graphql_client = GraphQLClient("http://example.com/graphql")

    route1 = graphql_mock.query("read_engagements_is_primary")
    route1.result = {
        "engagements": {
            "objects": [
                {
                    "validities": [
                        {
                            "is_primary": True,
                            "uuid": engagement_uuid,
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    route2 = graphql_mock.query("read_engagements")
    route2.result = {
        "engagements": {
            "objects": [
                {
                    "validities": [
                        {
                            "user_key": "Depressed Developer",
                            "extension_1": "An",
                            "extension_2": "obscure",
                            "extension_3": "cry",
                            "extension_4": "for",
                            "extension_5": "help",
                            "extension_6": "from",
                            "extension_7": "within",
                            "extension_8": "the",
                            "extension_9": "machine",
                            "extension_10": "!",
                            "leave_uuid": None,
                            "primary_uuid": uuid4(),
                            "job_function_uuid": uuid4(),
                            "org_unit_uuid": uuid4(),
                            "engagement_type_uuid": uuid4(),
                            "employee_uuid": employee_uuid,
                            "validity": {"from": "1970-01-01T00:00:00", "to": None},
                        }
                    ]
                }
            ]
        }
    }

    mo_routing_key = "engagement"
    await sync_tool.listen_to_changes_in_employees(
        employee_uuid,
        engagement_uuid,
        routing_key=mo_routing_key,
        delete=False,
        current_objects_only=True,
    )
    assert route1.called
    assert route2.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, "Engagement", delete=False
    )

    # Test expected behavior when unable to read any engagements
    old = route1.result
    route1.result = {"engagements": {"objects": []}}
    result = await sync_tool.listen_to_changes_in_employees(
        employee_uuid,
        engagement_uuid,
        routing_key=mo_routing_key,
        delete=False,
        current_objects_only=True,
    )
    assert result is None

    route1.result = old

    # Test expected behavior when unable to read engagement details
    route2.result = {"engagements": {"objects": []}}
    with pytest.raises(RequeueMessage) as exc:
        await sync_tool.listen_to_changes_in_employees(
            employee_uuid,
            engagement_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )
    assert "Unable to load mo object" in str(exc.value)


async def test_listen_to_changes_in_employees_skipped(
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    converted_ldap_object = LdapObject(dn="CN=foo")
    converter.to_ldap.return_value = converted_ldap_object

    employee_uuid = uuid4()
    address_uuid = uuid4()

    dataloader.find_mo_employee_dn.return_value = {"CN=foo"}

    mo_routing_key = "address"

    # Simulate an uuid which should be skipped
    # And an uuid which is too old, so it will be removed from the list
    old_uuid = uuid4()
    uuid_which_should_remain = uuid4()

    uuids_to_ignore = IgnoreMe()

    uuids_to_ignore.ignore_dict = {
        # This uuid should be ignored (once)
        str(address_uuid): [datetime.datetime.now(), datetime.datetime.now()],
        # This uuid has been here for too long, and should be removed
        str(old_uuid): [datetime.datetime(2020, 1, 1)],
        # This uuid should remain in the list
        str(uuid_which_should_remain): [datetime.datetime.now()],
    }

    sync_tool.uuids_to_ignore = uuids_to_ignore

    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_employees(
            employee_uuid,
            address_uuid,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )

        entries = [w for w in cap_logs if w["log_level"] == "info"]

        assert "Removing entry from ignore-dict" in entries[2]["event"]
        assert entries[2]["str_to_ignore"] == str(old_uuid)

        assert len(uuids_to_ignore) == 2  # Note that the old_uuid is removed by clean()
        assert len(uuids_to_ignore[old_uuid]) == 0
        assert len(uuids_to_ignore[uuid_which_should_remain]) == 1
        assert len(uuids_to_ignore[address_uuid]) == 1


async def test_listen_to_changes_in_employees_no_dn(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:
    payload = MagicMock()
    payload.uuid = uuid4()
    mo_routing_key: MORoutingKey = "person"
    dataloader.find_mo_employee_dn.return_value = set()
    dataloader.make_mo_employee_dn.side_effect = DNNotFound("Not found")

    with capture_logs() as cap_logs:
        with pytest.raises(RequeueMessage):
            await sync_tool.listen_to_changes_in_employees(
                payload.uuid,
                payload.object_uuid,
                routing_key=mo_routing_key,
                delete=False,
                current_objects_only=True,
            )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        last_log_message = messages[-1]["event"]

        assert last_log_message == "Unable to generate DN"


async def test_format_converted_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    employee_uuid = uuid4()

    engagement1 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2020-01-01",
    )

    engagement2 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="foo",
        from_date="2021-01-01",
    )

    # We do not expect this one the be uploaded, because its user_key exists twice in MO
    engagement3 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="duplicate_key",
        from_date="2021-01-01",
    )

    engagement1_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
    )

    engagement2_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="duplicate_key",
        from_date="2021-01-01",
    )

    engagement3_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="duplicate_key",
        from_date="2021-01-01",
    )

    dataloader.load_mo_employee_engagements.return_value = [
        engagement1_in_mo,
        engagement2_in_mo,
        engagement3_in_mo,
    ]

    json_key = "Engagement"

    converted_objects = [engagement1, engagement2, engagement3]

    operations = await sync_tool.format_converted_objects(
        converted_objects,
        json_key,
    )
    assert len(operations) == 2
    formatted_objects = [obj for obj, _ in operations]
    assert engagement3 not in formatted_objects
    assert first(formatted_objects).uuid == engagement1_in_mo.uuid
    assert first(formatted_objects).user_key == engagement1.user_key
    assert last(formatted_objects) == engagement2


async def test_format_converted_multiple_primary_engagements(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.find_mo_object_class.return_value = "Engagement"

    employee_uuid = uuid4()

    engagement1 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2020-01-01",
    )

    engagement2 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
    )

    dataloader.load_mo_employee_engagements.return_value = [engagement1, engagement2]

    dataloader.is_primaries.return_value = [True, True]

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
    converter.find_mo_object_class.return_value = "Employee"

    employee1 = Employee(cpr_no="1212121234")
    employee2 = Employee(cpr_no="1212121235")

    converted_objects = [employee1, employee2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects, "Employee"
    )

    assert formatted_objects[0][0] == employee1
    assert formatted_objects[1][0] == employee2


async def test_format_converted_employee_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    person_uuid = uuid4()
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", person_uuid=person_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", address_type_uuid, "2021-01-01", person_uuid=person_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", person_uuid=person_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_employee_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    # assert formatted_objects[1][0] == address2

    assert formatted_objects[0][0].uuid == address1_in_mo.uuid
    assert formatted_objects[0][0].value == "foo"  # type: ignore

    # Simulate that a matching employee for this address does not exist
    dataloader.load_mo_employee_addresses.side_effect = NoObjectsReturnedException("f")
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "Address")


async def test_format_converted_org_unit_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    org_unit_uuid = uuid4()
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    # assert formatted_objects[1][0] == address2

    assert formatted_objects[0][0].uuid == address1_in_mo.uuid
    assert formatted_objects[0][0].value == "foo"  # type: ignore

    # Simulate that a matching org unit for this address does not exist
    dataloader.load_mo_org_unit_addresses.side_effect = NoObjectsReturnedException("f")
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "Address")


async def test_format_converted_org_unit_address_objects_identical_to_mo(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    org_unit_uuid = uuid4()
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    # This one is identical to the one which we are trying to upload
    address1_in_mo = Address.from_simplified_fields(
        "foo", address_type_uuid, "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    operations = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )
    assert len(operations) == 2
    formatted_objects = [obj for obj, _ in operations]

    assert first(formatted_objects).value == "foo"  # type: ignore
    assert last(formatted_objects).value == "bar"  # type: ignore


async def test_format_converted_address_objects_without_person_or_org_unit(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    # These addresses have neither an org unit uuid or person uuid. we cannot convert
    # them
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields("foo", address_type_uuid, "2021-01-01")
    address2 = Address.from_simplified_fields("bar", address_type_uuid, "2021-01-01")

    converted_objects = [address1, address2]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert len(formatted_objects) == 0


async def test_format_converted_it_user_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "ITUser"
    converter.import_mo_object_class.return_value = ITUser

    it_user_in_mo = ITUser.from_simplified_fields(
        "Username1", uuid4(), "2021-01-01", person_uuid=uuid4()
    )

    dataloader.load_mo_employee_it_users.return_value = [it_user_in_mo]

    person_uuid = uuid4()
    it_system_uuid = uuid4()
    converted_objects = [
        ITUser.from_simplified_fields(
            "Username1", it_system_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username2", it_system_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "ITUser",
    )

    formatted_user_keys = [f[0].user_key for f in formatted_objects]
    # assert "Username1" not in formatted_user_keys
    assert "Username1" in formatted_user_keys
    assert "Username2" in formatted_user_keys
    assert len(formatted_objects) == 2  # was 1

    # Simulate that a matching employee for this it user does not exist
    dataloader.load_mo_employee_it_users.side_effect = NoObjectsReturnedException("f")
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, "ITUser")


async def test_format_converted_primary_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    employee_uuid = uuid4()
    primary_uuid = uuid4()
    engagement1_in_mo_uuid = uuid4()
    engagement2_in_mo_uuid = uuid4()

    converter.get_mo_attributes.return_value = ["user_key", "job_function"]
    converter.find_mo_object_class.return_value = "Engagement"
    converter.import_mo_object_class.return_value = Engagement

    async def is_primaries(uuids):
        return [uuid == engagement1_in_mo_uuid for uuid in uuids]

    dataloader.is_primaries = is_primaries

    engagement1 = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2020-01-01",
    )

    engagement1_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
        primary_uuid=primary_uuid,
        uuid=engagement1_in_mo_uuid,
    )

    # Engagement with the same user key. We should not update this one because it is
    # not primary.
    engagement2_in_mo = Engagement.from_simplified_fields(
        org_unit_uuid=uuid4(),
        person_uuid=employee_uuid,
        job_function_uuid=uuid4(),
        engagement_type_uuid=uuid4(),
        user_key="123",
        from_date="2021-01-01",
        primary_uuid=None,
        uuid=engagement2_in_mo_uuid,
    )

    dataloader.load_mo_employee_engagements.return_value = [
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
    assert formatted_objects[0][0].primary.uuid is not None  # type: ignore
    assert formatted_objects[0][0].user_key == "123"

    # Simulate that a matching employee for this engagement does not exist
    dataloader.load_mo_employee_engagements.side_effect = NoObjectsReturnedException(
        "f"
    )
    with pytest.raises(NoObjectsReturnedException):
        await sync_tool.format_converted_objects(converted_objects, json_key)


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_from_LDAP_ignore_twice(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    """
    When an uuid already is in the uuids_to_ignore dict, it should be added once more
    so it is ignored twice.
    """
    uuid = uuid4()
    mo_object_mock = MagicMock
    mo_object_mock.uuid = uuid
    converter.from_ldap.return_value = [mo_object_mock]

    uuids_to_ignore = IgnoreMe()
    uuids_to_ignore.ignore_dict = {str(uuid): [datetime.datetime.now()]}
    sync_tool.uuids_to_ignore = uuids_to_ignore

    assert len(sync_tool.uuids_to_ignore[uuid]) == 1
    await sync_tool.import_single_user("CN=foo")
    assert len(sync_tool.uuids_to_ignore[uuid]) == 2


async def test_import_single_object_from_LDAP_ignore_dn(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    dn_to_ignore = "CN=foo"
    ldap_object = LdapObject(dn=dn_to_ignore)
    dataloader.load_ldap_object.return_value = ldap_object
    sync_tool.dns_to_ignore.add(dn_to_ignore)

    with capture_logs() as cap_logs:
        await sync_tool.import_single_user("CN=foo")

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        last_log_message = messages[-1]["event"]
        assert last_log_message == "IgnoreChanges Exception"


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_from_LDAP_force(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    dn_to_ignore = "CN=foo"
    ldap_object = LdapObject(dn=dn_to_ignore)
    dataloader.load_ldap_object.return_value = ldap_object
    sync_tool.dns_to_ignore.add(dn_to_ignore)
    sync_tool.dns_to_ignore.add(dn_to_ignore)  # Ignore this DN twice

    uuid = uuid4()
    mo_object_mock = MagicMock
    mo_object_mock.uuid = uuid
    converter.from_ldap.return_value = [mo_object_mock]

    assert len(sync_tool.uuids_to_ignore[uuid]) == 0
    await sync_tool.import_single_user("CN=foo", force=False)
    assert len(sync_tool.uuids_to_ignore[uuid]) == 0
    await sync_tool.import_single_user("CN=foo", force=True)
    assert len(sync_tool.uuids_to_ignore[uuid]) == 1


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_from_LDAP_but_import_equals_false(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter._import_to_mo_.return_value = False

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
    converter.get_ldap_to_mo_json_keys.return_value = [
        "Address",
        "Engagement",
        "Employee",
    ]
    converter.from_ldap.return_value = [MagicMock()]  # list of (at least) one item
    # Act: run the method and collect logs
    with capture_logs() as cap_logs:
        await sync_tool.import_single_user("CN=foo")
        # Assert: verify that we process JSON keys in the expected order, regardless of
        # the original ordering.
        logged_json_keys: list[str] = [
            m["json_key"]
            for m in cap_logs
            if m.get("json_key") and "Loaded object" in m["event"]
        ]
        assert logged_json_keys == ["Employee", "Engagement", "Address"]


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_object_collects_engagement_uuid(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    """
    Test that the engagement UUID is saved when importing an engagement, and used when
    importing subsequent MO objects.
    """
    # Arrange
    converter.get_ldap_to_mo_json_keys.return_value = ["Engagement", "Address"]
    converter.from_ldap.return_value = [
        Engagement.from_simplified_fields(
            person_uuid=uuid4(),
            org_unit_uuid=uuid4(),
            job_function_uuid=uuid4(),
            engagement_type_uuid=uuid4(),
            user_key="user_key",
            from_date="2020-01-01",
        ),
        Address.from_simplified_fields(
            value="Address value",
            address_type_uuid=uuid4(),
            from_date="2020-01-01",
        ),
    ]
    # Act
    await sync_tool.import_single_user("CN=foo")
    # Assert
    from_ldap_args: list[tuple[str, UUID | None]] = [
        (call.args[1], call.kwargs["engagement_uuid"])
        for call in converter.from_ldap.call_args_list
    ]
    # Assert: first call to `from_ldap` is for "Employee", engagement UUID is None
    assert from_ldap_args[0][0] == "Employee"
    assert isinstance(from_ldap_args[0][1], AsyncMock)
    # Assert: second call to `from_ldap` is for "Engagement", engagement UUID is None
    assert from_ldap_args[1][0] == "Engagement"
    assert isinstance(from_ldap_args[1][1], AsyncMock)
    # Assert: third call to `from_ldap` is for "Address", engagement UUID is an UUID
    assert from_ldap_args[2][0] == "Address"
    assert isinstance(from_ldap_args[2][1], UUID)


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_single_user_logs_empty_engagement_uuid(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    # Arrange
    dataloader.find_mo_engagement_uuid.return_value = None
    with capture_logs() as cap_logs:
        # Act
        await sync_tool.import_single_user("CN=foo")
        # Assert
        logged_events: list[str] = [log["event"] for log in cap_logs]
        assert "Engagement UUID not found in MO" in logged_events


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_address_objects(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.find_mo_object_class.return_value = "ramodels.mo.details.address.Address"
    converter.import_mo_object_class.return_value = Address
    converter.get_mo_attributes.return_value = ["value", "uuid", "validity"]

    address_type_uuid = uuid4()
    person_uuid = uuid4()

    converted_objects = [
        Address.from_simplified_fields(
            "foo@bar.dk", address_type_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        Address.from_simplified_fields(
            "foo2@bar.dk", address_type_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        Address.from_simplified_fields(
            "foo3@bar.dk", address_type_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    formatted_objects = [
        (converted_object, Verb.CREATE) for converted_object in converted_objects
    ]

    converter.from_ldap.return_value = converted_objects

    with patch(
        "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
        return_value=formatted_objects,
    ):
        await sync_tool.import_single_user("CN=foo")
        dataloader.create_or_edit_mo_objects.assert_called_with(formatted_objects)

    with patch(
        "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
        side_effect=NoObjectsReturnedException("foo"),
    ):
        with capture_logs() as cap_logs:
            await sync_tool.import_single_user("CN=foo")

            messages = [w for w in cap_logs if w["log_level"] == "info"]
            assert "Could not format converted objects" in str(messages)

    # Simulate invalid phone number
    dataloader.create_or_edit_mo_objects.side_effect = HTTPStatusError(
        "invalid phone number", request=MagicMock(), response=MagicMock()
    )
    with capture_logs() as cap_logs:
        ignore_dict = copy.deepcopy(sync_tool.uuids_to_ignore.ignore_dict)
        await sync_tool.import_single_user("CN=foo")

        messages = [w for w in cap_logs if w["log_level"] == "warning"]
        assert "invalid phone number" in str(messages)

        # Make sure that no uuids are added to the ignore dict, if the import fails
        assert set(ignore_dict.keys()) == {
            key for key, val in sync_tool.uuids_to_ignore.ignore_dict.items() if val
        }


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_it_user_objects(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    converter.find_mo_object_class.return_value = "ramodels.mo.details.address.ITUser"
    converter.import_mo_object_class.return_value = ITUser
    converter.get_mo_attributes.return_value = ["user_key", "validity"]

    it_system_type1_uuid = uuid4()
    person_uuid = uuid4()

    converted_objects = [
        ITUser.from_simplified_fields(
            "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username2", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username3", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    converter.from_ldap.return_value = converted_objects

    it_user_in_mo = ITUser.from_simplified_fields(
        "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
    )

    it_users_in_mo = [it_user_in_mo]

    dataloader.load_mo_employee_it_users.return_value = it_users_in_mo

    await sync_tool.import_single_user("CN=foo")

    expected = [
        (converted_objects[0].user_key, it_user_in_mo.uuid, Verb.EDIT),
        (converted_objects[1].user_key, converted_objects[1].uuid, Verb.CREATE),
        (converted_objects[2].user_key, converted_objects[2].uuid, Verb.CREATE),
    ]

    actual = [
        (obj.user_key, obj.uuid, verb)
        for obj, verb in dataloader.create_or_edit_mo_objects.call_args.args[0]
    ]

    assert actual == expected


async def test_import_single_object_from_LDAP_non_existing_employee(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    dn = "CN=foo"

    ldap_connection = MagicMock()
    ldap_connection.response = [
        {"type": "searchResEntry", "attributes": {"EmployeeID": "0101011234"}, "dn": dn}
    ]
    context["user_context"]["ldap_connection"] = ldap_connection
    sync_tool.dataloader.load_ldap_cpr_object.return_value = [LdapObject(dn=dn)]  # type: ignore

    dataloader.find_mo_employee_uuid.return_value = None
    await sync_tool.import_single_user(dn)

    # Even though find_mo_employee_uuid does not return an uuid; it is generated
    assert type(converter.from_ldap.call_args_list[0].kwargs["employee_uuid"]) is UUID


async def test_ignoreMe():
    # Initialize empty ignore dict
    strings_to_ignore = IgnoreMe()
    assert len(strings_to_ignore) == 0

    # Add a string which should be ignored
    strings_to_ignore.add("ignore_me")
    assert len(strings_to_ignore) == 1
    assert len(strings_to_ignore["ignore_me"]) == 1

    # Raise an ignore exception so the string gets removed
    with pytest.raises(IgnoreChanges):
        strings_to_ignore.check("ignore_me")
    assert len(strings_to_ignore["ignore_me"]) == 0

    # Add an out-dated entry
    strings_to_ignore.ignore_dict = {
        "old_ignore_string": [datetime.datetime(1900, 1, 1)]
    }
    assert len(strings_to_ignore) == 1
    assert len(strings_to_ignore["old_ignore_string"]) == 1

    # Validate that it is gone after we clean
    strings_to_ignore.clean()
    assert len(strings_to_ignore) == 0
    assert len(strings_to_ignore["old_ignore_string"]) == 0

    # Add multiple out-dated entries
    strings_to_ignore.ignore_dict = {
        "old_ignore_string": [
            datetime.datetime(1900, 1, 1),
            datetime.datetime(1901, 1, 1),
            datetime.datetime(1902, 1, 1),
        ]
    }
    assert len(strings_to_ignore) == 1
    assert len(strings_to_ignore["old_ignore_string"]) == 3

    # Validate that they are all gone after we clean
    strings_to_ignore.clean()
    assert len(strings_to_ignore) == 0
    assert len(strings_to_ignore["old_ignore_string"]) == 0


async def test_remove_from_ignoreMe():
    # Initialize empty ignore dict
    strings_to_ignore = IgnoreMe()

    uuid = uuid4()
    strings_to_ignore.add(uuid)
    strings_to_ignore.add(uuid)

    timestamps = strings_to_ignore[uuid]

    assert len(strings_to_ignore[uuid]) == 2

    strings_to_ignore.remove(uuid)
    assert len(strings_to_ignore[uuid]) == 1
    assert strings_to_ignore[uuid][0] == min(timestamps)

    strings_to_ignore.remove(uuid)
    assert len(strings_to_ignore[uuid]) == 0


async def test_wait_for_export_to_finish(sync_tool: SyncTool):
    wait_for_export_to_finish = partial(sync_tool.wait_for_export_to_finish)

    @wait_for_export_to_finish
    async def decorated_func(self, payload):
        await asyncio.sleep(0.2)
        return

    async def regular_func(self, payload):
        await asyncio.sleep(0.2)
        return

    payload = MagicMock()
    payload.uuid = uuid4()

    different_payload = MagicMock()
    different_payload.uuid = uuid4()

    # Normally this would execute in 0.2 seconds + overhead
    t1 = time.time()
    await asyncio.gather(
        regular_func(sync_tool, payload),
        regular_func(sync_tool, payload),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.2
    assert elapsed_time < 0.3

    # But the decorator will make the second call wait for the first one to complete
    t1 = time.time()
    await asyncio.gather(
        decorated_func(sync_tool, payload),
        decorated_func(sync_tool, payload),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.4
    assert elapsed_time < 0.5

    # But only if payload.uuid is the same in both calls
    t1 = time.time()
    await asyncio.gather(
        decorated_func(sync_tool, payload),
        decorated_func(sync_tool, different_payload),
    )
    t2 = time.time()

    elapsed_time = t2 - t1

    assert elapsed_time >= 0.2
    assert elapsed_time < 0.3


def test_cleanup_needed(sync_tool: SyncTool):
    assert sync_tool.cleanup_needed([{"description": "success"}]) is True
    assert sync_tool.cleanup_needed([{"description": "PermissionDenied"}]) is False


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


@pytest.mark.parametrize(
    "object_type,function_name",
    [
        ("address", "address_refresh"),
        ("ituser", "ituser_refresh"),
        ("engagement", "engagement_refresh"),
    ],
)
async def test_refresh_object(
    sync_tool: SyncTool, dataloader: AsyncMock, object_type: str, function_name: str
) -> None:
    uuid = uuid4()

    dataloader.load_mo_object.return_value = {
        "payload": uuid,
        "parent_uuid": uuid,
        "object_type": object_type,
        "service_type": "employee",
    }
    await sync_tool.refresh_object(uuid, object_type)
    dataloader.load_mo_object.assert_awaited_once_with(str(uuid), object_type)

    refresh_function = getattr(dataloader.graphql_client, function_name)
    refresh_function.assert_awaited_once_with("os2mo_ldap_ie", uuid)


async def test_refresh_object_missing(
    sync_tool: SyncTool, dataloader: DataLoader
) -> None:
    dataloader.load_mo_object.return_value = None  # type: ignore

    uuid = uuid4()
    with pytest.raises(ValueError) as exc_info:
        await sync_tool.refresh_object(uuid, "address")
    assert f"Unable to look up address with UUID: {uuid}" in str(exc_info.value)


async def test_export_org_unit_addresses_on_engagement_change(
    sync_tool: SyncTool,
    dataloader: AsyncMock,
) -> None:
    engagement_uuid = uuid4()

    await sync_tool.export_org_unit_addresses_on_engagement_change(engagement_uuid)
    dataloader.graphql_client.engagement_org_unit_address_refresh.assert_called_with(
        "os2mo_ldap_ie",
        engagement_uuid,
    )


async def test_refresh_employee(
    sync_tool: SyncTool,
    dataloader: AsyncMock,
    converter: MagicMock,
):
    address_types = {
        uuid4(): "address_type 1",
        uuid4(): "address_type 2",
    }

    it_systems = {
        uuid4(): "it_system 1",
        uuid4(): "it_system 2",
    }

    # TODO: I believe these actually return string keys not uuids?
    converter.employee_address_type_info = address_types
    converter.it_system_info = it_systems

    employee_uuid = uuid4()
    await sync_tool.refresh_employee(employee_uuid)

    dataloader.graphql_client.person_address_refresh.assert_awaited_once_with(
        "os2mo_ldap_ie", employee_uuid, list(address_types.keys())
    )
    dataloader.graphql_client.person_engagement_refresh.assert_awaited_once_with(
        "os2mo_ldap_ie", employee_uuid
    )
    dataloader.graphql_client.person_ituser_refresh.assert_awaited_once_with(
        "os2mo_ldap_ie", employee_uuid, list(it_systems.keys())
    )


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_import_jobtitlefromadtomo_objects(
    context: Context,
    converter: MagicMock,
    dataloader: AsyncMock,
    sync_tool: SyncTool,
    fake_dn: DN,
) -> None:
    converter.find_mo_object_class.return_value = (
        "mo_ldap_import_export.customer_specific.JobTitleFromADToMO"
    )
    converter.import_mo_object_class.return_value = JobTitleFromADToMO
    converter.get_mo_attributes.return_value = ["user", "uuid", "job_function"]
    converter.get_ldap_to_mo_json_keys.return_value = [
        "Custom",
    ]

    user_uuid = uuid4()
    job_function_uuid = uuid4()
    job_function_fallback_uuid = uuid4()
    eng_uuid = str(uuid4())

    converted_objects = [
        JobTitleFromADToMO.from_simplified_fields(
            user_uuid=user_uuid,
            job_function_uuid=job_function_uuid,
            job_function_fallback_uuid=job_function_fallback_uuid,
        ),
    ]

    formatted_objects = [
        (converted_object, Verb.CREATE) for converted_object in converted_objects
    ]

    converter.from_ldap.return_value = converted_objects

    job = [{"uuid_to_ignore": eng_uuid, "task": AsyncMock()()}]

    context["legacy_graphql_session"] = AsyncMock()

    with patch(
        "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
        return_value=formatted_objects,
    ), patch(
        "mo_ldap_import_export.customer_specific.JobTitleFromADToMO.sync_to_mo",
        return_value=job,
    ):
        await sync_tool.import_single_user(fake_dn)
        dataloader.create_or_edit_mo_objects.assert_called_once()
        assert eng_uuid in sync_tool.uuids_to_ignore.ignore_dict


async def test_extract_uuid() -> None:
    uuid = uuid4()
    obj1 = uuid
    obj2 = Employee(uuid=uuid)

    self = object()

    @SyncTool.wait_for_export_to_finish
    async def dummy(*args, **kwargs):
        pass

    with capture_logs() as cap_logs:
        await dummy(self, obj1)
        assert str(uuid) in str(cap_logs)

    with capture_logs() as cap_logs:
        await dummy(self, obj2)
        assert str(uuid) in str(cap_logs)

    with pytest.raises(TypeError):
        await dummy(self, "foo")


def test_move_ldap_object(sync_tool: SyncTool, dataloader: AsyncMock):
    dataloader.move_ldap_object.return_value = True

    # user_context = {"dataloader": dataloader}
    old_dn = "CN=Angus,OU=Auchtertool"
    new_dn = "CN=Angus,OU=Dundee"

    # Attempt to move Angus from OU=Auchtertool to OU=Dundee
    ldap_object = sync_tool.move_ldap_object(LdapObject(dn=new_dn), old_dn)

    # Which means we need to create OU=Dundee
    dataloader.create_ou.assert_called_once_with("OU=Dundee")

    # Them move Angus
    dataloader.move_ldap_object.assert_called_once_with(old_dn, new_dn)

    # And delete OU=Auchtertool, which is now empty
    dataloader.delete_ou.assert_called_once_with("OU=Auchtertool")

    assert ldap_object.dn == new_dn


def test_move_ldap_object_move_failed(sync_tool: SyncTool, dataloader: AsyncMock):
    dataloader.move_ldap_object.return_value = False

    old_dn = "CN=Angus,OU=Auchtertool"
    new_dn = "CN=Angus,OU=Dundee"

    # Attempt to move Angus from OU=Auchtertool to OU=Dundee
    ldap_object = sync_tool.move_ldap_object(LdapObject(dn=new_dn), old_dn)

    # The move was not successful so we fall back to the old DN
    assert ldap_object.dn == old_dn
    dataloader.delete_ou.assert_not_called()


def test_move_ldap_object_nothing_to_move(sync_tool: SyncTool, dataloader: AsyncMock):
    old_dn = "CN=Angus,OU=Dundee"
    new_dn = "CN=Angus,OU=Dundee"

    # The new DN is equal to the old DN. We expect nothing to happen.
    ldap_object = sync_tool.move_ldap_object(LdapObject(dn=new_dn), old_dn)

    dataloader.create_ou.assert_not_called()
    dataloader.move_ldap_object.assert_not_called()
    dataloader.delete_ou.assert_not_called()
    assert ldap_object.dn == new_dn
    assert ldap_object.dn == old_dn


async def test_publish_engagements_for_org_unit(
    sync_tool: SyncTool, dataloader: AsyncMock
) -> None:
    uuid = OrgUnitUUID(uuid4())
    await sync_tool.publish_engagements_for_org_unit(uuid)
    dataloader.graphql_client.org_unit_engagements_refresh.assert_called_with(
        "os2mo_ldap_ie", uuid
    )


async def test_perform_import_checks_noop(sync_tool: SyncTool) -> None:
    """Test that perform_import_checks returns True when nothing is checked."""
    sync_tool.settings.check_holstebro_ou_issue_57426 = False
    result = await sync_tool.perform_import_checks("CN=foo", "Employee")
    assert result is True


@pytest.mark.usefixtures("fake_find_mo_employee_dn")
async def test_holstebro_import_checks(sync_tool: SyncTool, fake_dn: DN) -> None:
    with patch(
        "mo_ldap_import_export.import_export.SyncTool.perform_import_checks",
        return_value=False,
    ):
        with capture_logs() as cap_logs:
            await sync_tool.import_single_user(fake_dn, force=True)
            assert "Import checks executed" in str(cap_logs)


async def test_import_single_user_entity(sync_tool: SyncTool) -> None:
    sync_tool.converter.from_ldap.return_value = []  # type: ignore

    json_key = "Engagement"
    dn = "CN=foo"
    employee_uuid = uuid4()
    engagement_uuid = uuid4()
    with capture_logs() as cap_logs:
        result = await sync_tool.import_single_user_entity(
            json_key, dn, employee_uuid, engagement_uuid
        )
        assert result == engagement_uuid

        assert "No converted objects" in str(cap_logs)
