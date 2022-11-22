import os.path
import uuid
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastramqpi.context import Context
from ramodels.mo import Employee

from mo_ldap_import_export.converters import EmployeeConverter
from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.exceptions import CprNoNotFound
from mo_ldap_import_export.exceptions import IncorrectMapping

mapping = {
    "ldap_to_mo": {
        "user_attrs": {"givenname": "{{ldap.GivenName}}", "surname": "{{ldap.sn}}"}
    },
    "mo_to_ldap": {
        "user_attrs": {
            "givenName": "{{mo.givenname}}",
            "sn": "{{mo.surname}}",
            "displayName": "{{mo.surname}}, {{mo.givenname}}",
            "name": "{{mo.givenname}} {{mo.surname}}",
            "dn": "",
            "employeeID": "{{mo.cpr_no or None}}",
        }
    },
}

settings_mock = MagicMock()
settings_mock.ldap_organizational_unit = "foo"
settings_mock.ldap_search_base = "bar"

context: Context = {"user_context": {"mapping": mapping, "settings": settings_mock}}


def test_ldap_to_mo() -> None:
    converter = EmployeeConverter(context)
    employee = converter.from_ldap(
        LdapObject(
            dn="",
            name="",
            givenName="Tester",
            sn="Testersen",
            objectGUID="{" + str(uuid.uuid4()) + "}",
            cpr="0101011234",
        )
    )
    assert employee.givenname == "Tester"
    assert employee.surname == "Testersen"


def test_mo_to_ldap() -> None:
    converter = EmployeeConverter(context)
    ldap_object: Any = converter.to_ldap(
        Employee(givenname="Tester", surname="Testersen")
    )
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.name == "Tester Testersen"


def test_mapping_loader() -> None:
    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )
    expected = {
        "ldap_to_mo": {
            "user_attrs": {
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
            "user_attrs": {
                "givenName": "{{mo.givenname}}",
                "sn": "{{mo.surname}}",
                "displayName": "{{mo.surname}}, {{mo.givenname}}",
                "name": "{{mo.givenname}} {{mo.surname}}",
                "cpr": "{{mo.cpr_no or None}}",
                "seniority": "{{mo.seniority or None}}",
                "nickname_givenname": "{{mo.nickname_givenname or None}}",
                "nickname_surname": "{{mo.nickname_surname or None}}",
            }
        },
    }
    assert mapping == expected


def test_mapping_loader_failure() -> None:

    good_mapping = {
        "ldap_to_mo": {
            "user_attrs": {
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
            "user_attrs": {
                "givenName": "{{mo.givenname}}",
                "sn": "{{mo.surname}}",
                "displayName": "{{mo.surname}}, {{mo.givenname}}",
                "name": "{{mo.givenname}} {{mo.surname}}",
                "cpr": "{{mo.cpr_no or None}}",
                "seniority": "{{mo.seniority or None}}",
                "nickname_givenname": "{{mo.nickname_givenname or None}}",
                "nickname_surname": "{{mo.nickname_surname or None}}",
            }
        },
    }

    for bad_mapping in ({}, {"ldap_to_mo": {}}, {"mo_to_ldap": {}}):
        with pytest.raises(IncorrectMapping):
            EmployeeConverter(
                context={
                    "user_context": {"mapping": bad_mapping, "settings": settings_mock}
                }
            )
        with pytest.raises(IncorrectMapping):
            EmployeeConverter(
                context={
                    "user_context": {"mapping": bad_mapping, "settings": settings_mock}
                }
            )

        converter = EmployeeConverter(
            context={
                "user_context": {"mapping": good_mapping, "settings": settings_mock}
            }
        )
        converter.mapping = bad_mapping
        with pytest.raises(IncorrectMapping):
            converter.from_ldap(
                LdapObject(
                    dn="",
                    name="",
                    givenName="Tester",
                    sn="Testersen",
                    objectGUID="{" + str(uuid.uuid4()) + "}",
                    cpr="0101011234",
                )
            )
        with pytest.raises(IncorrectMapping):
            converter.to_ldap(Employee(givenname="Tester", surname="Testersen"))


def test_splitfirst() -> None:
    assert EmployeeConverter.filter_splitfirst("Test") == ["Test", ""]
    assert EmployeeConverter.filter_splitfirst("Test Testersen") == [
        "Test",
        "Testersen",
    ]
    assert EmployeeConverter.filter_splitfirst("Test Testersen med test") == [
        "Test",
        "Testersen med test",
    ]
    assert EmployeeConverter.filter_splitfirst("") == ["", ""]


def test_splitlast() -> None:
    assert EmployeeConverter.filter_splitlast("Test") == ["", "Test"]
    assert EmployeeConverter.filter_splitlast("Test Testersen") == ["Test", "Testersen"]
    assert EmployeeConverter.filter_splitlast("Test Testersen med test") == [
        "Test Testersen med",
        "test",
    ]
    assert EmployeeConverter.filter_splitlast("") == ["", ""]


def test_find_cpr_field() -> None:

    # This mapping is accepted
    good_mapping = {
        "mo_to_ldap": {
            "user_attrs": {
                "employeeID": "{{mo.cpr_no or None}}",
            }
        },
    }

    # This mapping does not contain the mo.cpr_no field
    bad_mapping = {
        "mo_to_ldap": {
            "user_attrs": {
                "givenName": "{{mo.givenname}}",
            }
        },
    }

    # Test both cases
    for mapping in good_mapping, bad_mapping:
        context: Context = {
            "user_context": {"mapping": mapping, "settings": settings_mock}
        }
        try:
            converter = EmployeeConverter(context)
        except Exception as e:
            assert type(e) == CprNoNotFound
            assert e.status_code == 404
        else:
            assert converter.cpr_field == "employeeID"


def test_template_lenience() -> None:

    mapping = {
        "ldap_to_mo": {
            "user_attrs": {"givenname": "{{ldap.GivenName}}", "surname": "{{ldap.sn}}"}
        },
        "mo_to_ldap": {
            "user_attrs": {
                "givenName": "{{mo.givenname}}",
                "sn": "{{mo.surname}}",
                "displayName": "{{mo.surname}}, {{mo.givenname}}",
                "name": "{{mo.givenname}} {{mo.surname}}",
                "dn": "",
                "employeeID": "{{mo.cpr_no or None}}",
            }
        },
    }

    converter = EmployeeConverter(
        context={"user_context": {"mapping": mapping, "settings": settings_mock}}
    )
    converter.from_ldap(
        LdapObject(
            dn="",
            cpr="1234567890",
        )
    )
