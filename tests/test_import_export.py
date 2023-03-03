import asyncio
import datetime
import os
import re
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from ramodels.mo.details.address import Address
from ramodels.mo.details.engagement import Engagement
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from structlog.testing import capture_logs

from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.import_export import format_converted_objects
from mo_ldap_import_export.import_export import import_single_user
from mo_ldap_import_export.import_export import listen_to_changes_in_employees
from mo_ldap_import_export.import_export import listen_to_changes_in_org_units
from mo_ldap_import_export.ldap_classes import LdapObject


async def test_listen_to_changes_in_org_units(converter: MagicMock):

    org_unit_info = {uuid4(): {"name": "Magenta Aps"}}

    dataloader = MagicMock()
    dataloader.load_mo_org_units.return_value = org_unit_info

    payload = MagicMock()
    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    mo_routing_key = MORoutingKey.build("org_unit.org_unit.edit")

    await listen_to_changes_in_org_units(
        context,
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
    load_mo_employees_in_org_unit.return_value = [employee1, employee2]
    load_mo_org_unit_addresses.return_value = [address]

    dataloader.modify_ldap_object = modify_ldap_object
    dataloader.load_mo_address = load_mo_address
    dataloader.load_mo_employees_in_org_unit = load_mo_employees_in_org_unit
    dataloader.load_mo_org_unit_addresses = load_mo_org_unit_addresses

    converter.find_ldap_object_class.return_value = "user"

    payload = MagicMock()
    context = Context(
        {
            "user_context": {
                "dataloader": dataloader,
                "converter": converter,
            }
        }
    )

    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await listen_to_changes_in_org_units(
            context,
            payload,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )

    # Assert that an address was uploaded to two ldap objects.
    assert modify_ldap_object.await_count == 2


async def test_listen_to_change_in_org_unit_address_not_supported(
    dataloader: AsyncMock, load_settings_overrides: dict[str, str], converter: MagicMock
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

    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    with pytest.raises(NotSupportedException):
        await listen_to_changes_in_org_units(
            context,
            payload,
            routing_key=mo_routing_key,
            delete=False,
            current_objects_only=True,
        )


async def test_listen_to_changes_in_employees(
    dataloader: AsyncMock,
    load_settings_overrides: dict[str, str],
    test_mo_address: Address,
) -> None:

    settings_mock = MagicMock()
    settings_mock.ldap_search_base = "bar"

    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )

    converter = MagicMock()
    converter.cpr_field = "EmployeeID"
    converted_ldap_object = LdapObject(dn="Foo")
    converter.to_ldap.return_value = converted_ldap_object
    converter.mapping = {"mo_to_ldap": {"EmailEmployee": 2}}
    converter.get_it_system_user_key.return_value = "AD"

    address_type_user_key = "EmailEmployee"
    converter.get_address_type_user_key.return_value = address_type_user_key

    it_system_type_name = "AD"

    context = Context(
        {
            "user_context": {
                "settings": settings_mock,
                "mapping": mapping,
                "converter": converter,
                "dataloader": dataloader,
            }
        }
    )
    payload = MagicMock()
    payload.uuid = uuid4()
    payload.object_uuid = uuid4()

    settings = MagicMock()
    settings.ldap_search_base = "DC=bar"

    # Simulate a created employee
    mo_routing_key = MORoutingKey.build("employee.employee.create")
    with patch("mo_ldap_import_export.import_export.cleanup", AsyncMock()):
        await asyncio.gather(
            listen_to_changes_in_employees(
                context,
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
            listen_to_changes_in_employees(
                context,
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
            listen_to_changes_in_employees(
                context,
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
            listen_to_changes_in_employees(
                context,
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

    uuids_to_ignore = {
        # This uuid should be ignored (once)
        payload.object_uuid: [datetime.datetime.now(), datetime.datetime.now()],
        # This uuid has been here for too long, and should be removed
        old_uuid: [datetime.datetime(2020, 1, 1)],
        # This uuid should remain in the list
        uuid_which_should_remain: [datetime.datetime.now()],
    }

    with patch("mo_ldap_import_export.import_export.uuids_to_ignore", uuids_to_ignore):
        with capture_logs() as cap_logs:
            await asyncio.gather(
                listen_to_changes_in_employees(
                    context,
                    payload,
                    routing_key=mo_routing_key,
                    delete=False,
                    current_objects_only=True,
                ),
            )

            entries = [w for w in cap_logs if w["log_level"] == "info"]

            assert re.match(
                f"Removing timestamp belonging to {old_uuid} from uuids_to_ignore.",
                entries[1]["event"],
            )
            assert re.match(f".*Ignoring .*{payload.object_uuid}", entries[2]["event"])
            assert len(uuids_to_ignore) == 3
            assert len(uuids_to_ignore[old_uuid]) == 0
            assert len(uuids_to_ignore[uuid_which_should_remain]) == 1
            assert len(uuids_to_ignore[payload.object_uuid]) == 1


async def test_format_converted_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock
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

    user_context = {"converter": converter, "dataloader": dataloader}

    json_key = "Engagement"

    converted_objects = [engagement1, engagement2, engagement3]

    formatted_objects = await format_converted_objects(
        converted_objects, json_key, user_context
    )

    assert len(formatted_objects) == 2
    assert engagement3 not in formatted_objects
    assert formatted_objects[1] == engagement2
    assert formatted_objects[0].uuid == engagement1_in_mo.uuid
    assert formatted_objects[0].user_key == engagement1.user_key


async def test_format_converted_employee_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.find_mo_object_class.return_value = "Employee"
    user_context = {"converter": converter, "dataloader": dataloader}

    employee1 = Employee(cpr_no="1212121234")
    employee2 = Employee(cpr_no="1212121235")

    converted_objects = [employee1, employee2]

    formatted_objects = await format_converted_objects(
        converted_objects, "Employee", user_context
    )

    assert formatted_objects[0] == employee1
    assert formatted_objects[1] == employee2


async def test_format_converted_employee_address_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}

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

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert formatted_objects[1] == address2

    assert formatted_objects[0].uuid == address1_in_mo.uuid
    assert formatted_objects[0].value == "foo"


async def test_format_converted_org_unit_address_objects(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}
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

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert formatted_objects[1] == address2

    assert formatted_objects[0].uuid == address1_in_mo.uuid
    assert formatted_objects[0].value == "foo"


async def test_format_converted_org_unit_address_objects_identical_to_mo(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}
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

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert formatted_objects[0].value == "bar"
    assert len(formatted_objects) == 1


async def test_format_converted_address_objects_without_person_or_org_unit(
    converter: MagicMock, dataloader: AsyncMock
):

    converter.get_mo_attributes.return_value = ["value", "address_type"]
    converter.find_mo_object_class.return_value = "Address"
    converter.import_mo_object_class.return_value = Address

    user_context = {"converter": converter, "dataloader": dataloader}

    # These addresses have neither an org unit uuid or person uuid. we cannot convert
    # them
    address_type_uuid = uuid4()
    address1 = Address.from_simplified_fields("foo", address_type_uuid, "2021-01-01")
    address2 = Address.from_simplified_fields("bar", address_type_uuid, "2021-01-01")

    converted_objects = [address1, address2]

    formatted_objects = await format_converted_objects(
        converted_objects, "Address", user_context
    )

    assert len(formatted_objects) == 0


async def test_format_converted_primary_engagement_objects(
    converter: MagicMock, dataloader: AsyncMock
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

    user_context = {"converter": converter, "dataloader": dataloader}

    json_key = "Engagement"

    converted_objects = [engagement1]

    formatted_objects = await format_converted_objects(
        converted_objects, json_key, user_context
    )

    assert len(formatted_objects) == 1
    assert formatted_objects[0].primary.uuid is not None
    assert formatted_objects[0].user_key == "123"


async def test_import_single_object_from_LDAP_ignore_twice(
    converter: MagicMock, dataloader: AsyncMock
) -> None:
    """
    When an uuid already is in the uuids_to_ignore dict, it should be added once more
    so it is ignored twice.
    """

    uuid = uuid4()
    mo_object_mock = MagicMock
    mo_object_mock.uuid = uuid
    converter.from_ldap.return_value = [mo_object_mock]

    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    uuids_to_ignore = {uuid: [datetime.datetime.now()]}
    with patch("mo_ldap_import_export.import_export.uuids_to_ignore", uuids_to_ignore):
        await asyncio.gather(import_single_user("0101011234", context))
        assert len(uuids_to_ignore[uuid]) == 2


async def test_import_single_object_from_LDAP_but_import_equals_false(
    converter: MagicMock, dataloader: AsyncMock
):
    converter.__import_to_mo__.return_value = False
    context = Context(
        {"user_context": {"dataloader": dataloader, "converter": converter}}
    )

    with capture_logs() as cap_logs:
        await asyncio.gather(import_single_user("0101011234", context))

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        for message in messages:
            assert re.match(
                "__import_to_mo__ == False",
                message["event"],
            )
