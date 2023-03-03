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
from ramodels.mo.employee import Employee
from ramqp.mo.models import MORoutingKey
from structlog.testing import capture_logs

from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.ldap_classes import LdapObject
from mo_ldap_import_export.main import listen_to_changes_in_employees
from mo_ldap_import_export.main import listen_to_changes_in_org_units


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
