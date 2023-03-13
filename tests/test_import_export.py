import asyncio
import datetime
import re
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ramodels.mo.details.address import Address
from ramodels.mo.details.engagement import Engagement
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from structlog.testing import capture_logs

from mo_ldap_import_export.exceptions import IgnoreChanges
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.import_export import IgnoreMe
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.ldap_classes import LdapObject


@pytest.fixture
def context(dataloader: AsyncMock, converter: MagicMock) -> Context:
    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )
    return context


@pytest.fixture
def sync_tool(context: Context) -> SyncTool:
    sync_tool = SyncTool(context)
    return sync_tool


async def test_listen_to_changes_in_org_units(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):

    org_unit_info = {uuid4(): {"name": "Magenta Aps"}}

    dataloader.load_mo_org_units = MagicMock()
    dataloader.load_mo_org_units.return_value = org_unit_info

    payload = MagicMock()

    mo_routing_key = MORoutingKey.build("org_unit.org_unit.edit")

    await sync_tool.listen_to_changes_in_org_units(
        payload,
        routing_key=mo_routing_key,
        delete=False,
        current_objects_only=True,
    )
    assert converter.org_unit_info == org_unit_info


async def test_listen_to_change_in_org_unit_address(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    converter: MagicMock,
    sync_tool: SyncTool,
):
    mo_routing_key = MORoutingKey.build("org_unit.address.edit")

    address = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")
    employee1 = Employee(cpr_no="0101011234")
    employee2 = Employee(cpr_no="0101011235")

    load_mo_address = AsyncMock()
    load_mo_employees_in_org_unit = AsyncMock()
    load_mo_org_unit_addresses = AsyncMock()
    modify_ldap_object = AsyncMock()

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

    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await sync_tool.listen_to_changes_in_org_units(
            payload,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )

    # Assert that an address was uploaded to two ldap objects
    # (even though load_mo_employees_in_org_unit returned three employee objects)
    assert modify_ldap_object.await_count == 2

    load_mo_employees_in_org_unit.return_value = [Employee()]

    with capture_logs() as cap_logs:
        await sync_tool.listen_to_changes_in_org_units(
            payload,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            "Employee does not have a cpr no",
            messages[-1]["event"],
        )


async def test_listen_to_change_in_org_unit_address_not_supported(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    converter: MagicMock,
    sync_tool: SyncTool,
):
    """
    Mapping an organization unit address to non-employee objects is not supported.
    """
    mo_routing_key = MORoutingKey.build("org_unit.address.edit")
    payload = MagicMock()
    address = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")

    def find_ldap_object_class(json_key):
        d = {"Employee": "user", "LocationUnit": "address"}
        return d[json_key]

    converter.find_ldap_object_class.side_effect = find_ldap_object_class

    load_mo_address = AsyncMock()
    load_mo_address.return_value = address
    dataloader.load_mo_address = load_mo_address

    converter.address_type_info = {
        str(address.address_type.uuid): {"user_key": "LocationUnit"}
    }

    with pytest.raises(NotSupportedException):
        await sync_tool.listen_to_changes_in_org_units(
            payload,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )


async def test_listen_to_changes_in_employees(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:

    settings_mock = MagicMock()
    settings_mock.ldap_search_base = "bar"

    converter.cpr_field = "EmployeeID"
    converted_ldap_object = LdapObject(dn="Foo")
    converter.to_ldap.return_value = converted_ldap_object
    converter.mapping = {"mo_to_ldap": {"EmailEmployee": 2}}
    converter.get_it_system_user_key.return_value = "AD"

    address_type_user_key = "EmailEmployee"
    converter.get_address_type_user_key.return_value = address_type_user_key

    it_system_type_name = "AD"

    payload = MagicMock()
    payload.uuid = uuid4()
    payload.object_uuid = uuid4()

    settings = MagicMock()
    settings.ldap_search_base = "DC=bar"

    # Simulate a created employee
    mo_routing_key = MORoutingKey.build("employee.employee.create")
    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await asyncio.gather(
            sync_tool.listen_to_changes_in_employees(
                payload,
                routing_key=mo_routing_key,
                delete=False,
                current_objects_only=True,
            ),
        )
    assert dataloader.load_mo_employee.called
    assert converter.to_ldap.called
    assert dataloader.modify_ldap_object.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, "Employee", overwrite=True, delete=False
    )
    assert not dataloader.load_mo_address.called

    # Simulate a created address
    mo_routing_key = MORoutingKey.build("employee.address.create")
    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await asyncio.gather(
            sync_tool.listen_to_changes_in_employees(
                payload,
                routing_key=mo_routing_key,
                delete=False,
                current_objects_only=True,
            ),
        )
    assert dataloader.load_mo_address.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, address_type_user_key, delete=False
    )

    # Simulate a created IT user
    mo_routing_key = MORoutingKey.build("employee.it.create")
    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await asyncio.gather(
            sync_tool.listen_to_changes_in_employees(
                payload,
                routing_key=mo_routing_key,
                delete=False,
                current_objects_only=True,
            ),
        )
    assert dataloader.load_mo_it_user.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, it_system_type_name, delete=False
    )

    # Simulate a created engagement
    mo_routing_key = MORoutingKey.build("employee.engagement.create")
    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await asyncio.gather(
            sync_tool.listen_to_changes_in_employees(
                payload,
                routing_key=mo_routing_key,
                delete=False,
                current_objects_only=True,
            ),
        )
    assert dataloader.load_mo_engagement.called
    dataloader.modify_ldap_object.assert_called_with(
        converted_ldap_object, "Engagement", delete=False
    )

    # Simulate an uuid which should be skipped
    # And an uuid which is too old, so it will be removed from the list
    old_uuid = uuid4()
    uuid_which_should_remain = uuid4()

    uuids_to_ignore = IgnoreMe()

    uuids_to_ignore.ignore_dict = {
        # This uuid should be ignored (once)
        str(payload.object_uuid): [datetime.datetime.now(), datetime.datetime.now()],
        # This uuid has been here for too long, and should be removed
        str(old_uuid): [datetime.datetime(2020, 1, 1)],
        # This uuid should remain in the list
        str(uuid_which_should_remain): [datetime.datetime.now()],
    }

    sync_tool.uuids_to_ignore = uuids_to_ignore

    with capture_logs() as cap_logs:
        with pytest.raises(IgnoreChanges, match=f".*Ignoring .*{payload.object_uuid}"):
            await asyncio.gather(
                sync_tool.listen_to_changes_in_employees(
                    payload,
                    routing_key=mo_routing_key,
                    delete=False,
                    current_objects_only=True,
                ),
            )

        entries = [w for w in cap_logs if w["log_level"] == "info"]

        assert re.match(
            f"Removing .* belonging to {old_uuid} from ignore_dict",
            entries[1]["event"],
        )
        assert len(uuids_to_ignore) == 2  # Note that the old_uuid is removed by clean()
        assert len(uuids_to_ignore[old_uuid]) == 0
        assert len(uuids_to_ignore[uuid_which_should_remain]) == 1
        assert len(uuids_to_ignore[payload.object_uuid]) == 1


async def test_listen_to_changes_in_employees_no_cpr(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
    sync_tool: SyncTool,
    converter: MagicMock,
) -> None:

    settings_mock = MagicMock()
    settings_mock.ldap_search_base = "bar"

    payload = MagicMock()
    payload.uuid = uuid4()
    payload.object_uuid = uuid4()

    settings = MagicMock()
    settings.ldap_search_base = "DC=bar"

    employee_without_cpr = Employee()
    dataloader.load_mo_employee.return_value = employee_without_cpr

    # Simulate a created employee
    mo_routing_key = MORoutingKey.build("employee.employee.create")

    with capture_logs() as cap_logs:
        await asyncio.gather(
            sync_tool.listen_to_changes_in_employees(
                payload,
                routing_key=mo_routing_key,
                delete=False,
                current_objects_only=True,
            ),
        )

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            "Employee does not have a cpr no",
            messages[-1]["event"],
        )


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

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        json_key,
    )

    assert len(formatted_objects) == 2
    assert engagement3 not in formatted_objects
    assert formatted_objects[1] == engagement2
    assert formatted_objects[0].uuid == engagement1_in_mo.uuid
    assert formatted_objects[0].user_key == engagement1.user_key


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

    assert formatted_objects[0] == employee1
    assert formatted_objects[1] == employee2


async def test_format_converted_employee_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    person_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", person_uuid=person_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", uuid4(), "2021-01-01", person_uuid=person_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", person_uuid=person_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_employee_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[1] == address2

    assert formatted_objects[0].uuid == address1_in_mo.uuid
    assert formatted_objects[0].value == "foo"


async def test_format_converted_org_unit_address_objects(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    org_unit_uuid = uuid4()
    address1 = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", org_unit_uuid=org_unit_uuid
    )
    address2 = Address.from_simplified_fields(
        "bar", uuid4(), "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    address1_in_mo = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", org_unit_uuid=org_unit_uuid
    )

    converted_objects = [address1, address2]

    dataloader.load_mo_org_unit_addresses.return_value = [address1_in_mo]

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[1] == address2

    assert formatted_objects[0].uuid == address1_in_mo.uuid
    assert formatted_objects[0].value == "foo"


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

    formatted_objects = await sync_tool.format_converted_objects(
        converted_objects,
        "Address",
    )

    assert formatted_objects[0].value == "bar"
    assert len(formatted_objects) == 1


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

    def is_primary(uuid):
        if uuid == engagement1_in_mo_uuid:
            return True
        else:
            return False

    dataloader.is_primary.side_effect = is_primary

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
    assert formatted_objects[0].primary.uuid is not None
    assert formatted_objects[0].user_key == "123"


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

    await asyncio.gather(sync_tool.import_single_user("0101011234"))
    assert len(sync_tool.uuids_to_ignore[uuid]) == 2


async def test_import_single_object_from_LDAP_ignore_dn(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    dn_to_ignore = "CN=foo"
    ldap_object = LdapObject(dn=dn_to_ignore)
    dataloader.load_ldap_cpr_object.return_value = ldap_object
    sync_tool.dns_to_ignore.add(dn_to_ignore)

    with capture_logs() as cap_logs:
        await asyncio.gather(sync_tool.import_single_user("0101011234"))

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            f"\\[check_ignore_dict\\] Ignoring {dn_to_ignore}",
            messages[-1]["event"].detail,
        )


async def test_import_single_object_from_LDAP_but_import_equals_false(
    converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.__import_to_mo__.return_value = False

    with capture_logs() as cap_logs:
        await asyncio.gather(sync_tool.import_single_user("0101011234"))

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        for message in messages:
            assert re.match(
                "__import_to_mo__ == False",
                message["event"],
            )


async def test_import_single_object_from_LDAP_multiple_employees(
    context: Context, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:

    dataloader.load_ldap_cpr_object.return_value = None
    dataloader.load_ldap_cpr_object.side_effect = MultipleObjectsReturnedException(
        "foo"
    )

    with capture_logs() as cap_logs:
        await asyncio.gather(sync_tool.import_single_user("0101011234"))

        warnings = [w for w in cap_logs if w["log_level"] == "warning"]

        assert re.match(
            ".*Could not upload .* object.*",
            warnings[0]["event"],
        )


async def test_import_address_objects(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
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

    converter.from_ldap.return_value = converted_objects

    with patch(
        "mo_ldap_import_export.import_export.SyncTool.format_converted_objects",
        return_value=converted_objects,
    ):
        await asyncio.gather(sync_tool.import_single_user("0101011234"))
        dataloader.upload_mo_objects.assert_called_with(converted_objects)


async def test_import_it_user_objects(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
):
    converter.find_mo_object_class.return_value = "ramodels.mo.details.address.ITUser"
    converter.import_mo_object_class.return_value = ITUser
    converter.get_mo_attributes.return_value = ["user_key", "validity"]

    it_system_type1_uuid = uuid4()
    it_system_type2_uuid = uuid4()
    person_uuid = uuid4()

    converted_objects = [
        ITUser.from_simplified_fields(
            "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username2", it_system_type2_uuid, "2021-01-01", person_uuid=person_uuid
        ),
        ITUser.from_simplified_fields(
            "Username3", it_system_type2_uuid, "2021-01-01", person_uuid=person_uuid
        ),
    ]

    converter.from_ldap.return_value = converted_objects

    it_user_in_mo = ITUser.from_simplified_fields(
        "Username1", it_system_type1_uuid, "2021-01-01", person_uuid=person_uuid
    )

    it_users_in_mo = [it_user_in_mo]

    dataloader.load_mo_employee_it_users.return_value = it_users_in_mo

    await asyncio.gather(sync_tool.import_single_user("0101011234"))

    non_existing_converted_objects = [
        converted_objects[1],
        converted_objects[2],
    ]

    dataloader.upload_mo_objects.assert_called_with(non_existing_converted_objects)


async def test_import_single_object_from_LDAP_non_existing_employee(
    context: Context, converter: MagicMock, dataloader: AsyncMock, sync_tool: SyncTool
) -> None:
    dataloader.find_mo_employee_uuid.return_value = None
    await asyncio.gather(sync_tool.import_single_user("0101011234"))

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
