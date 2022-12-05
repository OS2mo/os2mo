import copy
import datetime
import os.path
import re
import uuid
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from fastramqpi.context import Context
from ramodels.mo import Employee
from structlog.testing import capture_logs

from mo_ldap_import_export.converters import find_cpr_field
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.exceptions import CprNoNotFound
from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.exceptions import NotSupportedException


@pytest.fixture
def context() -> Context:

    mapping = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "givenname": "{{ldap.GivenName}}",
                "surname": "{{ldap.sn}}",
            },
            "Email": {
                "objectClass": "ramodels.mo.details.address.Address",
                "value": "{{ldap.mail or None}}",
                "type": "{{'address'}}",
                "validity": "{{ dict(from_date = ldap.mail_validity_from|strftime) }}",
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
    mo_address_types = {"uuid1": "Email", "uuid2": "Post"}

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

    overview = {"user": {"attributes": list(dataloader.single_value.keys())}}

    dataloader.load_ldap_overview.return_value = overview

    context: Context = {
        "user_context": {
            "mapping": mapping,
            "settings": settings_mock,
            "dataloader": dataloader,
        }
    }
    return context


@pytest.fixture
def converter(context: Context) -> LdapConverter:
    return LdapConverter(context)


def test_ldap_to_mo(context: Context) -> None:
    converter = LdapConverter(context)
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
    )[0]
    assert employee.givenname == "Tester"
    assert employee.surname == "Testersen"

    mail = converter.from_ldap(
        LdapObject(
            dn="",
            mail="foo@bar.dk",
            mail_validity_from=datetime.datetime(2019, 1, 1, 0, 10, 0),
        ),
        "Email",
    )[0]

    assert mail.value == "foo@bar.dk"
    from_date = mail.validity.dict()["from_date"].replace(tzinfo=None)
    assert from_date == datetime.datetime(2019, 1, 1, 0, 10, 0)


def test_mo_to_ldap(context: Context) -> None:
    converter = LdapConverter(context)
    obj_dict: dict = {"mo_employee": Employee(givenname="Tester", surname="Testersen")}
    ldap_object: Any = converter.to_ldap(obj_dict, "Employee")
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.name == "Tester Testersen"

    with pytest.raises(NotSupportedException):
        obj_dict = {"mo_address": "foo"}
        converter.to_ldap(obj_dict, "Employee")


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
                "givenname": "{{ldap.GivenName}}",
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


async def test_check_mapping(context: Context):

    context = copy.deepcopy(context)

    def initialize_converter():
        # find_cpr_field = MagicMock()
        context["user_context"]["mapping"] = mapping
        with patch(
            "mo_ldap_import_export.converters.find_cpr_field",
            return_value="employeeID",
        ):
            LdapConverter(context)

    def test_exception(match):

        with pytest.raises(IncorrectMapping, match=match):
            initialize_converter()

    # Testing missing mo_to_ldap key
    mapping: dict = {}
    test_exception("Missing key: 'mo_to_ldap'")

    # Testing missing ldap_to_mo key
    mapping["mo_to_ldap"] = {}
    test_exception("Missing key: 'ldap_to_mo'")

    # This dict is accepted
    mapping["ldap_to_mo"] = {}
    initialize_converter()

    # Test invalid json keys
    mapping["ldap_to_mo"] = {"Foo": {}}
    mapping["mo_to_ldap"] = {"Foo": {}}
    test_exception("'Foo' is not a valid key")

    # Test no objectClass present
    mapping["ldap_to_mo"] = {
        "Email": {
            "value": "foo",
        }
    }
    mapping["mo_to_ldap"] = {
        "Email": {
            "value": "foo",
        }
    }
    test_exception("'objectClass' key not present")

    # Test invalid mo object attributes
    mapping["ldap_to_mo"] = {
        "Email": {
            "objectClass": "ramodels.mo.details.address.Address",
            "value": "foo",
        }
    }
    mapping["mo_to_ldap"] = {
        "Email": {
            "objectClass": "user",
            "value": "foo",
        }
    }
    test_exception(
        "attribute .* is mandatory. The following attributes are mandatory: .*"
    )

    # Test invalid ldap object attributes
    mapping["ldap_to_mo"] = {
        "Employee": {
            "objectClass": "ramodels.mo.employee.Employee",
        }
    }
    mapping["mo_to_ldap"] = {"Employee": {"objectClass": "user", "foo": "bar"}}
    test_exception("attribute 'foo' not allowed")

    # Test cpr field not present
    mapping["mo_to_ldap"] = {"Employee": {"objectClass": "user", "name": "bar"}}
    test_exception("'employeeID' attribute not present")

    # Test single_value field
    mapping["mo_to_ldap"] = {
        "Email": {"objectClass": "user", "employeeID": "123", "postalAddress": "123"}
    }
    mapping["ldap_to_mo"] = {
        "Email": {
            "objectClass": "ramodels.mo.details.address.Address",
            "value": "{{ldap.mail or None}}",
            "validity": "{{ dict(from_date = ldap.mail_validity_from|strftime) }}",
            "address_type": (
                "{{ dict(uuid=" "'f376deb8-4743-4ca6-a047-3241de8fe9d2') }}"
            ),
        },
    }
    with capture_logs() as cap_logs:
        initialize_converter()
        warnings = [w for w in cap_logs if w["log_level"] == "warning"]
        assert len(warnings) == 1
        assert re.match(
            ".*LDAP attribute cannot contain multiple values.*", warnings[0]["event"]
        )

    # Test value in ldap_to_mo not present in mo_to_ldap
    mapping["ldap_to_mo"] = {"Employee": {}}
    mapping["mo_to_ldap"] = {}
    test_exception("Missing key in 'mo_to_ldap'")

    # Test value in mo_to_ldap not present in ldap_to_mo
    mapping["ldap_to_mo"] = {}
    mapping["mo_to_ldap"] = {"Employee": {}}
    test_exception("Missing key in 'ldap_to_mo'")


def test_nonejoin(converter: LdapConverter):
    output = converter.nonejoin("foo", "bar", None)
    assert output == "foo, bar"


def test_str_to_dict(converter: LdapConverter):
    output = converter.str_to_dict("{'foo':2}")
    assert output == {"foo": 2}


def test_filter_strftime(converter: LdapConverter):
    output = converter.filter_strftime(datetime.datetime(2019, 4, 13, 20, 10, 10))
    assert output == "2019-04-13T20:10:10"


def test_get_number_of_entries(converter: LdapConverter):

    single_entry_object = LdapObject(dn="foo", value="bar")
    multi_entry_object = LdapObject(dn="foo", value=["bar", "bar2"])

    output = converter.get_number_of_entries(single_entry_object)
    assert output == 1

    output = converter.get_number_of_entries(multi_entry_object)
    assert output == 2
