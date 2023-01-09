import copy
import datetime
import os.path
import re
import uuid
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from jinja2 import Environment
from jinja2 import Undefined
from ramodels.mo import Employee
from ramodels.mo.details.address import Address
from structlog.testing import capture_logs

from mo_ldap_import_export.converters import find_cpr_field
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.exceptions import CprNoNotFound
from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.exceptions import NotSupportedException


@pytest.fixture
def context() -> Context:

    mapping = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "givenname": "{{ldap.givenName}}",
                "surname": "{{ldap.sn}}",
                "cpr_no": "{{ldap.employeeID or None}}",
            },
            "Email": {
                "objectClass": "ramodels.mo.details.address.Address",
                "value": "{{ldap.mail or None}}",
                "type": "{{'address'}}",
                "validity": (
                    "{{ dict(from_date = " "ldap.mail_validity_from|mo_datestring) }}"
                ),
                "address_type": (
                    "{{ dict(uuid=" "'f376deb8-4743-4ca6-a047-3241de8fe9d2') }}"
                ),
            },
        },
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "givenName": "{{mo_employee.givenname}}",
                "sn": "{{mo_employee.surname}}",
                "displayName": "{{mo_employee.surname}}, {{mo_employee.givenname}}",
                "name": "{{mo_employee.givenname}} {{mo_employee.surname}}",
                "dn": "",
                "employeeID": "{{mo_employee.cpr_no or None}}",
            },
            "Email": {
                "objectClass": "user",
                "employeeID": "{{mo_employee.cpr_no or None}}",
            },
        },
    }

    settings_mock = MagicMock()
    settings_mock.ldap_organizational_unit = "foo"
    settings_mock.ldap_search_base = "bar"

    dataloader = MagicMock()
    mo_address_types = {
        "Email": {"uuid": "uuid1", "scope": "MAIL"},
        "Post": {"uuid": "uuid2", "scope": "TEXT"},
    }

    load_mo_address_types = MagicMock()
    load_mo_address_types.return_value = mo_address_types
    dataloader.load_mo_address_types = load_mo_address_types
    dataloader.single_value = {
        "givenName": True,
        "sn": True,
        "displayName": True,
        "name": True,
        "dn": True,
        "employeeID": True,
        "postalAddress": False,
        "mail": True,
    }

    find_mo_employee_uuid_sync = MagicMock()
    find_mo_employee_uuid_sync.return_value = uuid.UUID(
        hex="{135c46ae-3b0e-4679-8318-40b73d9cedf3}"
    )
    dataloader.find_mo_employee_uuid_sync = find_mo_employee_uuid_sync

    overview = {"user": {"attributes": list(dataloader.single_value.keys())}}

    dataloader.load_ldap_overview.return_value = overview

    context: Context = {
        "user_context": {
            "mapping": mapping,
            "settings": settings_mock,
            "dataloader": dataloader,
            "username_generator": MagicMock(),
        }
    }

    return context


@pytest.fixture
def converter(context: Context) -> LdapConverter:
    return LdapConverter(context)


def test_ldap_to_mo(converter: LdapConverter) -> None:
    # converter = LdapConverter(context)
    employee_uuid = uuid4()
    employee = converter.from_ldap(
        LdapObject(
            dn="",
            name="",
            givenName="Tester",
            sn="Testersen",
            objectGUID="{" + str(uuid.uuid4()) + "}",
            cpr="0101011234",
        ),
        "Employee",
        employee_uuid=employee_uuid,
    )[0]
    assert employee.givenname == "Tester"
    assert employee.surname == "Testersen"
    assert employee.uuid == employee_uuid

    mail = converter.from_ldap(
        LdapObject(
            dn="",
            mail="foo@bar.dk",
            mail_validity_from=datetime.datetime(2019, 1, 1, 0, 10, 0),
        ),
        "Email",
        employee_uuid=employee_uuid,
    )[0]

    assert mail.value == "foo@bar.dk"
    assert mail.person.uuid == employee_uuid
    from_date = mail.validity.dict()["from_date"].replace(tzinfo=None)

    # Note: Date is always at midnight in MO
    assert from_date == datetime.datetime(2019, 1, 1, 0, 0, 0)


def test_ldap_to_mo_no_uuid(context: Context) -> None:
    converter = LdapConverter(context)
    employee_uuid = uuid4()
    employee = converter.from_ldap(
        LdapObject(
            dn="",
            name="",
            givenName="Tester",
            sn="Testersen",
            objectGUID="{" + str(uuid.uuid4()) + "}",
            employeeID="0101011234",  # Must have a CPR number
        ),
        "Employee",
    )[0]
    assert employee.givenname == "Tester"
    assert employee.surname == "Testersen"
    assert employee.uuid is not None
    assert employee.uuid != employee_uuid
    # Same uuid as in fixture
    assert employee.uuid == uuid.UUID(hex="{135c46ae-3b0e-4679-8318-40b73d9cedf3}")


def test_mo_to_ldap(converter: LdapConverter) -> None:
    obj_dict: dict = {"mo_employee": Employee(givenname="Tester", surname="Testersen")}
    ldap_object: Any = converter.to_ldap(obj_dict, "Employee", dn="foo")
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.name == "Tester Testersen"
    assert ldap_object.dn == "foo"

    with pytest.raises(NotSupportedException):
        obj_dict = {"mo_address": "foo"}
        converter.to_ldap(obj_dict, "Employee")


def test_mo_to_ldap_dn_is_None_obj_exists(converter: LdapConverter) -> None:
    obj_dict: dict = {"mo_employee": Employee(givenname="Tester", surname="Testersen")}

    dataloader = MagicMock()
    dataloader.load_ldap_cpr_object.return_value = LdapObject(dn="foo123")
    converter.dataloader = dataloader

    ldap_object: Any = converter.to_ldap(obj_dict, "Employee", dn=None)
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.name == "Tester Testersen"
    assert ldap_object.dn == "foo123"


def test_mo_to_ldap_dn_is_None_obj_does_not_exist(converter: LdapConverter) -> None:
    obj_dict: dict = {"mo_employee": Employee(givenname="Tester", surname="Testersen")}

    dataloader = MagicMock()
    dataloader.load_ldap_cpr_object.return_value = LdapObject(dn="foo123")
    dataloader.load_ldap_cpr_object.side_effect = NoObjectsReturnedException("foo")

    converter.dataloader = dataloader

    username_generator = MagicMock()
    username_generator.generate_dn.return_value = "foo456"
    converter.username_generator = username_generator

    ldap_object: Any = converter.to_ldap(obj_dict, "Employee", dn=None)
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.name == "Tester Testersen"
    assert ldap_object.dn == "foo456"


def test_mapping_loader() -> None:
    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )
    expected = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "givenname": "{{ldap.givenName or ldap.name|splitlast|first}}",
                "surname": "{{ldap.surname or ldap.sn or "
                "ldap.name|splitlast|last or ''}}",
                "cpr_no": "{{ldap.cpr or None}}",
                "seniority": "{{ldap.seniority or None}}",
                "nickname_givenname": "{{ldap.nickname_givenname or None}}",
                "nickname_surname": "{{ldap.nickname_surname or None}}",
            }
        },
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "givenName": "{{mo_employee.givenname}}",
                "sn": "{{mo_employee.surname}}",
                "displayName": "{{mo_employee.surname}}, {{mo_employee.givenname}}",
                "name": "{{mo_employee.givenname}} {{mo_employee.surname}}",
                "cpr": "{{mo_employee.cpr_no or None}}",
                "seniority": "{{mo_employee.seniority or None}}",
                "nickname_givenname": "{{mo_employee.nickname_givenname or None}}",
                "nickname_surname": "{{mo_employee.nickname_surname or None}}",
            }
        },
    }
    assert mapping == expected


def test_mapping_loader_failure(context: Context) -> None:

    good_context = copy.deepcopy(context)

    for bad_mapping in ({}, {"ldap_to_mo": {}}, {"mo_to_ldap": {}}):

        bad_context = copy.deepcopy(context)
        bad_context["user_context"]["mapping"] = bad_mapping

        with pytest.raises(IncorrectMapping):
            LdapConverter(context=bad_context)
        with pytest.raises(IncorrectMapping):
            LdapConverter(context=bad_context)

        converter = LdapConverter(context=good_context)
        converter.mapping = bad_mapping
        with pytest.raises(IncorrectMapping):
            converter.from_ldap(
                LdapObject(
                    dn="",
                    name="",
                    givenName="Tester",
                    sn="Testersen",
                    objectGUID="{" + str(uuid.uuid4()) + "}",
                    employeeID="0101011234",
                ),
                "Employee",
            )[0]
        with pytest.raises(IncorrectMapping):
            obj_dict = {
                "mo_employee": Employee(givenname="Tester", surname="Testersen")
            }
            converter.to_ldap(obj_dict, "Employee")


def test_splitfirst() -> None:
    assert LdapConverter.filter_splitfirst("Test") == ["Test", ""]
    assert LdapConverter.filter_splitfirst("Test Testersen") == [
        "Test",
        "Testersen",
    ]
    assert LdapConverter.filter_splitfirst("Test Testersen med test") == [
        "Test",
        "Testersen med test",
    ]
    assert LdapConverter.filter_splitfirst("") == ["", ""]


def test_splitlast() -> None:
    assert LdapConverter.filter_splitlast("Test") == ["", "Test"]
    assert LdapConverter.filter_splitlast("Test Testersen") == ["Test", "Testersen"]
    assert LdapConverter.filter_splitlast("Test Testersen med test") == [
        "Test Testersen med",
        "test",
    ]
    assert LdapConverter.filter_splitlast("") == ["", ""]


def test_strip_non_digits() -> None:
    assert LdapConverter.filter_strip_non_digits("01-01-01-1234") == "0101011234"
    assert LdapConverter.filter_strip_non_digits("01/01/01-1234") == "0101011234"
    assert LdapConverter.filter_strip_non_digits("010101-1234") == "0101011234"
    assert LdapConverter.filter_strip_non_digits(101011234) is None


def test_find_cpr_field(context: Context) -> None:

    # This mapping is accepted
    good_mapping = {
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "employeeID": "{{mo_employee.cpr_no or None}}",
            }
        },
        "ldap_to_mo": {"Employee": {"objectClass": "ramodels.mo.employee.Employee"}},
    }

    # This mapping does not contain the mo_employee.cpr_no field
    bad_mapping = {
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "givenName": "{{mo_employee.givenname}}",
            }
        },
        "ldap_to_mo": {"Employee": {"objectClass": "ramodels.mo.employee.Employee"}},
    }

    # Test both cases
    context["user_context"]["mapping"] = good_mapping
    converter = LdapConverter(context)
    assert converter.cpr_field == "employeeID"

    with pytest.raises(CprNoNotFound):
        with patch(
            "mo_ldap_import_export.converters.LdapConverter.check_mapping",
            return_value=None,
        ):
            context["user_context"]["mapping"] = bad_mapping
            converter = LdapConverter(context)
            find_cpr_field(converter.mapping)

    with pytest.raises(IncorrectMapping):
        with patch(
            "mo_ldap_import_export.converters.LdapConverter.check_mapping",
            return_value=None,
        ):
            # This mapping does not contain the 'Employee' field
            context["user_context"]["mapping"] = {"mo_to_ldap": {}}
            converter = LdapConverter(context)
            find_cpr_field(converter.mapping)


def test_template_lenience(context: Context) -> None:

    mapping = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "givenname": "{{ldap.givenName}}",
                "surname": "{{ldap.sn}}",
            }
        },
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "givenName": "{{mo_employee.givenname}}",
                "sn": "{{mo_employee.surname}}",
                "displayName": "{{mo_employee.surname}}, {{mo_employee.givenname}}",
                "name": "{{mo_employee.givenname}} {{mo_employee.surname}}",
                "dn": "",
                "employeeID": "{{mo_employee.cpr_no or None}}",
            }
        },
    }

    context["user_context"]["mapping"] = mapping
    converter = LdapConverter(context)
    converter.from_ldap(
        LdapObject(
            dn="",
            cpr="1234567890",
        ),
        "Employee",
    )[0]


def test_find_object_class(converter: LdapConverter):

    output = converter.find_object_class("Employee", "ldap_to_mo")
    assert output == "ramodels.mo.employee.Employee"

    output = converter.find_object_class("Employee", "mo_to_ldap")
    assert output == "user"

    with pytest.raises(IncorrectMapping):
        converter.find_object_class("non_existing_json_key", "mo_to_ldap")


def test_find_ldap_object_class(converter: LdapConverter):
    object_class = converter.find_ldap_object_class("Employee")
    assert object_class == "user"


def test_find_mo_object_class(converter: LdapConverter):
    object_class = converter.find_mo_object_class("Employee")
    assert object_class == "ramodels.mo.employee.Employee"


def test_get_ldap_attributes(converter: LdapConverter, context: Context):
    attributes = converter.get_ldap_attributes("Employee")

    all_attributes = list(
        context["user_context"]["mapping"]["mo_to_ldap"]["Employee"].keys()
    )

    expected_attributes = [a for a in all_attributes if a != "objectClass"]

    assert attributes == expected_attributes


def test_get_mo_attributes(converter: LdapConverter, context: Context):
    attributes = converter.get_mo_attributes("Employee")

    all_attributes = list(
        context["user_context"]["mapping"]["ldap_to_mo"]["Employee"].keys()
    )

    expected_attributes = [a for a in all_attributes if a != "objectClass"]

    assert attributes == expected_attributes


def test_check_attributes(converter: LdapConverter):
    detected_attributes = ["foo", "bar"]
    accepted_attributes = ["bar"]

    with pytest.raises(IncorrectMapping):
        converter.check_attributes(detected_attributes, accepted_attributes)


def test_get_accepted_json_keys(converter: LdapConverter):
    output = converter.get_accepted_json_keys()
    assert output == ["Employee", "Email", "Post"]


def test_nonejoin(converter: LdapConverter):
    output = converter.nonejoin("foo", "bar", None)
    assert output == "foo, bar"


def test_str_to_dict(converter: LdapConverter):
    output = converter.str_to_dict("{'foo':2}")
    assert output == {"foo": 2}


def test_filter_mo_datestring(converter: LdapConverter):
    output = converter.filter_mo_datestring(datetime.datetime(2019, 4, 13, 20, 10, 10))
    # Note: Dates are always at midnight in MO
    assert output == "2019-04-13T00:00:00"


def test_get_number_of_entries(converter: LdapConverter):

    single_entry_object = LdapObject(dn="foo", value="bar")
    multi_entry_object = LdapObject(dn="foo", value=["bar", "bar2"])

    output = converter.get_number_of_entries(single_entry_object)
    assert output == 1

    output = converter.get_number_of_entries(multi_entry_object)
    assert output == 2


async def test_cross_check_keys(converter: LdapConverter):

    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_to_ldap_json_keys",
        return_value=["foo", "bar"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_to_mo_json_keys",
        return_value=["bar"],
    ):
        with pytest.raises(IncorrectMapping, match="Missing key in 'ldap_to_mo'"):
            converter.cross_check_keys()

    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_to_ldap_json_keys",
        return_value=["foo"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_to_mo_json_keys",
        return_value=["foo", "bar"],
    ):
        with pytest.raises(IncorrectMapping, match="Missing key in 'mo_to_ldap'"):
            converter.cross_check_keys()


async def test_check_key_validity(converter: LdapConverter):
    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_to_ldap_json_keys",
        return_value=["foo", "bar"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_to_mo_json_keys",
        return_value=["foo", "bar"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_accepted_json_keys",
        return_value=["foo"],
    ):
        with pytest.raises(IncorrectMapping, match="'bar' is not a valid key"):
            converter.check_key_validity()


async def test_check_for_objectClass(converter: LdapConverter):
    converter.raw_mapping = {
        "ldap_to_mo": {"foo": {"objectClass": "foo"}},
        "mo_to_ldap": {"foo": {}},
    }
    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_json_keys",
        return_value=["foo"],
    ):
        with pytest.raises(IncorrectMapping, match="'objectClass' key not present"):
            converter.check_for_objectClass()


async def test_check_mo_attributes(converter: LdapConverter):
    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_to_mo_json_keys",
        return_value=["foo"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.import_mo_object_class",
        return_value=Address,
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_attributes",
        return_value=["value"],
    ):
        with pytest.raises(
            IncorrectMapping,
            match=(
                "attribute .* is mandatory. The following attributes are mandatory: .*"
            ),
        ):
            converter.check_mo_attributes()


async def test_check_ldap_attributes_cpr_field(converter: LdapConverter):

    dataloader = MagicMock()
    dataloader.load_ldap_overview.return_value = {
        "user": {"attributes": ["attr1", "attr2"]}
    }
    converter.dataloader = dataloader

    patch(
        "mo_ldap_import_export.converters.LdapConverter.dataloader.load_ldap_overview",
        return_value={"user": {"attributes": ["attr1", "attr2"]}},
    ),
    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_to_ldap_json_keys",
        return_value=["foo"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_attributes",
        return_value=["attr1", "foo"],
    ), patch(
        "mo_ldap_import_export.converters.find_cpr_field",
        return_value="cpr_field",
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.check_attributes",
        return_value=None,
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.find_ldap_object_class",
        return_value="user",
    ):
        with pytest.raises(
            IncorrectMapping,
            match="'cpr_field' attribute not present",
        ):
            converter.check_ldap_attributes()


async def test_check_ldap_attributes_single_value_fields(converter: LdapConverter):

    dataloader = MagicMock()
    dataloader.load_ldap_overview.return_value = {
        "user": {"attributes": ["attr1", "attr2"]}
    }
    dataloader.single_value = {"attr1": True, "cpr_field": False}
    converter.dataloader = dataloader
    environment = Environment(undefined=Undefined)

    mapping = {
        "mo_to_ldap": {
            "foo": {"attr1": "{{ mo_address.value }}", "cpr_field": "{{ foo }}"}
        }
    }
    converter.mapping = converter._populate_mapping_with_templates(mapping, environment)

    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_to_ldap_json_keys",
        return_value=["foo"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_attributes",
        return_value=["attr1", "cpr_field"],
    ), patch(
        "mo_ldap_import_export.converters.find_cpr_field",
        return_value="cpr_field",
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.check_attributes",
        return_value=None,
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.find_ldap_object_class",
        return_value="user",
    ):
        with capture_logs() as cap_logs:
            converter.check_ldap_attributes()

            warnings = [w for w in cap_logs if w["log_level"] == "warning"]
            assert len(warnings) == 1
            assert re.match(
                ".*LDAP attribute cannot contain multiple values.*",
                warnings[0]["event"],
            )


async def test_check_dar_scope(converter: LdapConverter):

    address_type_info = {"foo": {"scope": "TEXT"}, "bar": {"scope": "DAR"}}
    converter.address_type_info = address_type_info

    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_to_mo_json_keys",
        return_value=["foo", "bar"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.find_mo_object_class",
        return_value="ramodels.mo.details.address.Address",
    ):
        with pytest.raises(
            IncorrectMapping,
            match="maps to an address with scope = 'DAR'",
        ):
            converter.check_dar_scope()


async def test_get_address_type_uuid(converter: LdapConverter):

    address_type_info = {"foo": {"uuid": "uuid1"}, "bar": {"uuid": "uuid2"}}
    converter.address_type_info = address_type_info

    assert converter.get_address_type_uuid("foo") == "uuid1"
    assert converter.get_address_type_uuid("bar") == "uuid2"


async def test_get_it_system_uuid(converter: LdapConverter):
    it_system_info = {"AD": {"uuid": "uuid1"}, "Office365": {"uuid": "uuid2"}}
    converter.it_system_info = it_system_info

    assert converter.get_it_system_uuid("AD") == "uuid1"
    assert converter.get_it_system_uuid("Office365") == "uuid2"


def test_get_it_system(converter: LdapConverter):
    it_system_info = {
        "AD": {"uuid": "uuid1", "name": "AD"},
        "Office365": {"uuid": "uuid2", "name": "Office365"},
    }
    converter.it_system_info = it_system_info

    assert converter.get_it_system("uuid1")["name"] == "AD"
    assert converter.get_it_system("uuid2")["name"] == "Office365"


async def test_check_ldap_to_mo_references(converter: LdapConverter):

    converter.raw_mapping = {
        "ldap_to_mo": {"Employee": {"name": "{{ ldap.nonExistingAttribute}}"}}
    }

    with patch(
        "mo_ldap_import_export.converters.LdapConverter.get_ldap_to_mo_json_keys",
        return_value=["Employee"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.find_ldap_object_class",
        return_value="user",
    ):
        with pytest.raises(
            IncorrectMapping,
            match="Non existing attribute detected",
        ):
            converter.check_ldap_to_mo_references()
