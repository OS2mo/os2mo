# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
import datetime
import os
from collections.abc import Iterator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
import yaml
from ramodels.mo.details.address import Address
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.employee import Employee

from mo_ldap_import_export.ldap_classes import LdapObject


@pytest.fixture
def settings_overrides() -> Iterator[dict[str, str]]:
    """Fixture to construct dictionary of minimal overrides for valid settings.

    Yields:
        Minimal set of overrides.
    """
    overrides = {
        "CLIENT_ID": "Foo",
        "CLIENT_SECRET": "bar",
        "LDAP_CONTROLLERS": '[{"host": "localhost"}]',
        "LDAP_DOMAIN": "LDAP",
        "LDAP_USER": "foo",
        "LDAP_PASSWORD": "foo",
        "LDAP_SEARCH_BASE": "DC=ad,DC=addev",
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
        if os.environ.get(key) is None:
            monkeypatch.setenv(key, value)
    yield settings_overrides


@pytest.fixture
def test_mo_address() -> Address:
    test_mo_address = Address.from_simplified_fields(
        "foo@bar.dk", uuid4(), "2021-01-01"
    )
    return test_mo_address


@pytest.fixture
def test_mo_objects() -> list:
    return [
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": datetime.datetime.today().strftime("%Y-%m-%d"),
                "to": None,
            },
        },
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": "2021-01-01",
                "to": datetime.datetime.today().strftime("%Y-%m-%d"),
            },
        },
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": "2021-01-01",
                "to": "2021-05-01",
            },
        },
        {
            "uuid": uuid4(),
            "service_type": "employee",
            "payload": uuid4(),
            "parent_uuid": uuid4(),
            "object_type": "person",
            "validity": {
                "from": datetime.datetime.today().strftime("%Y-%m-%d"),
                "to": datetime.datetime.today().strftime("%Y-%m-%d"),
            },
        },
    ]


@pytest.fixture
def dataloader(
    sync_dataloader: MagicMock, test_mo_address: Address, test_mo_objects: list
) -> AsyncMock:

    test_ldap_object = LdapObject(
        name="Tester", Department="QA", dn="someDN", EmployeeID="0101012002"
    )
    test_mo_employee = Employee(cpr_no="1212121234")

    test_mo_it_user = ITUser.from_simplified_fields("foo", uuid4(), "2021-01-01")

    load_ldap_cpr_object = MagicMock()
    load_ldap_cpr_object.return_value = test_ldap_object

    dataloader = AsyncMock()
    dataloader.load_ldap_object = sync_dataloader
    dataloader.load_ldap_OUs = sync_dataloader
    dataloader.load_ldap_populated_overview = sync_dataloader
    dataloader.load_ldap_overview = sync_dataloader
    dataloader.load_ldap_cpr_object = load_ldap_cpr_object
    dataloader.load_ldap_objects.return_value = [test_ldap_object] * 3
    dataloader.load_mo_employee.return_value = test_mo_employee
    dataloader.load_mo_address.return_value = test_mo_address
    dataloader.load_mo_it_user.return_value = test_mo_it_user
    dataloader.load_mo_employee_address_types.return_value = {}
    dataloader.load_mo_org_unit_address_types.return_value = {}
    dataloader.load_mo_it_systems.return_value = {}
    dataloader.load_mo_primary_types.return_value = {}
    dataloader.load_mo_employee_addresses.return_value = [test_mo_address] * 2
    dataloader.load_all_mo_objects.return_value = test_mo_objects
    dataloader.load_mo_object.return_value = test_mo_objects[0]
    dataloader.load_ldap_attribute_values = sync_dataloader
    dataloader.modify_ldap_object.return_value = [{"description": "success"}]
    dataloader.get_ldap_objectGUID = sync_dataloader
    dataloader.find_or_make_mo_employee_dn.return_value = ["CN=foo"]
    dataloader.find_dn_by_engagement_uuid.return_value = "CN=foo"

    dataloader.load_ldap_OUs = MagicMock()
    dataloader.move_ldap_object = MagicMock()
    dataloader.delete_ou = MagicMock()
    dataloader.create_ou = MagicMock()

    return dataloader


@pytest.fixture
def sync_dataloader() -> MagicMock:

    dataloader = MagicMock()
    return dataloader


@pytest.fixture
def converter() -> MagicMock:
    converter = MagicMock()
    converter.get_accepted_json_keys.return_value = [
        "Employee",
        "Address",
        "EmailEmployee",
    ]
    converter.cpr_field = "EmployeeID"
    converter._import_to_mo_ = MagicMock()
    converter._import_to_mo_.return_value = True

    converter.to_ldap = AsyncMock()
    converter.from_ldap = AsyncMock()
    converter.to_ldap.return_value = LdapObject(dn="CN=foo", name="Angus")

    converter.get_employee_address_type_user_key = AsyncMock()
    converter.get_org_unit_address_type_user_key = AsyncMock()
    converter.get_it_system_user_key = AsyncMock()
    converter.get_engagement_type_name = AsyncMock()
    converter.get_job_function_name = AsyncMock()
    converter.get_org_unit_name = AsyncMock()

    return converter


@pytest.fixture
def settings() -> MagicMock:
    return MagicMock()


@pytest.fixture
def username_generator() -> MagicMock:
    return MagicMock()


@pytest.fixture
def sync_tool() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def internal_amqpsystem() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def export_checks() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def import_checks() -> AsyncMock:
    return AsyncMock()


def read_mapping(filename):
    """
    Read a json mapping file
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "mo_ldap_import_export",
        "mappings",
        filename,
    )
    with open(file_path) as file:
        return yaml.safe_load(file)
