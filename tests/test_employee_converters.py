import os.path
import uuid

from ramodels.mo import Employee

from mo_ldap_import_export.converters import EmployeeConverter
from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.dataloaders import LdapEmployee

mapping = {
    "ldap_to_mo": {
        "user_attrs": {"givenname": "{{ldap.GivenName}}", "surname": "{{ldap.sn}}"}
    },
    "mo_to_ldap": {
        "user_attrs": {
            "givenName": "{{mo.givenname}}",
            "sn": "{{mo.surname}}",
            "displayName": "{{mo.surname}}, {{mo.givenname}}",
            "Name": "{{mo.givenname}} {{mo.surname}}",
            "dn": "",
        }
    },
}


def test_ldap_to_mo() -> None:
    converter = EmployeeConverter(mapping)
    employee = converter.from_ldap(
        LdapEmployee(
            dn="",
            Name="",
            givenName="Tester",
            sn="Testersen",
            objectGUID="{" + str(uuid.uuid4()) + "}",
        )
    )
    assert employee.givenname == "Tester"
    assert employee.surname == "Testersen"


def test_mo_to_ldap() -> None:
    converter = EmployeeConverter(mapping)
    ldap_object = converter.to_ldap(Employee(givenname="Tester", surname="Testersen"))
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.Name == "Tester Testersen"


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


def test_splitlast() -> None:
    assert EmployeeConverter.filter_splitlast("Test") == ["", "Test"]
    assert EmployeeConverter.filter_splitlast("Test Testersen") == ["Test", "Testersen"]
    assert EmployeeConverter.filter_splitlast("Test Testersen med test") == [
        "Test Testersen med",
        "test",
    ]
