import copy
import datetime
import os.path
import re
import uuid
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pandas as pd
import pytest
from fastramqpi.context import Context
from jinja2 import Environment
from jinja2 import Undefined
from ramodels.mo import Employee
from ramodels.mo.details.engagement import Engagement
from structlog.testing import capture_logs

from mo_ldap_import_export.converters import find_cpr_field
from mo_ldap_import_export.converters import find_ldap_it_system
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.converters import read_mapping_json
from mo_ldap_import_export.dataloaders import LdapObject
from mo_ldap_import_export.exceptions import IncorrectMapping
from mo_ldap_import_export.exceptions import InvalidNameException
from mo_ldap_import_export.exceptions import NotSupportedException
from mo_ldap_import_export.exceptions import UUIDNotFoundException


@pytest.fixture
def context() -> Context:

    mapping = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "__import_to_mo__": True,
                "givenname": "{{ldap.givenName}}",
                "surname": "{{ldap.sn}}",
                "cpr_no": "{{ldap.employeeID or None}}",
                "uuid": "{{ employee_uuid or NONE }}",
            },
            "Email": {
                "objectClass": "ramodels.mo.details.address.Address",
                "__import_to_mo__": True,
                "value": "{{ldap.mail}}",
                "type": "{{'address'}}",
                "validity": (
                    "{{ dict(from_date = " "ldap.mail_validity_from|mo_datestring) }}"
                ),
                "address_type": (
                    "{{ dict(uuid=" "'f376deb8-4743-4ca6-a047-3241de8fe9d2') }}"
                ),
                "person": "{{ dict(uuid=employee_uuid or NONE) }}",
            },
            "Active Directory": {
                "objectClass": "ramodels.mo.details.it_system.ITUser",
                "__import_to_mo__": True,
                "user_key": "{{ ldap.msSFU30Name or NONE }}",
                "itsystem": "{{ dict(uuid=get_it_system_uuid(ldap.itSystemName)) }}",
                "validity": "{{ dict(from_date=now()|mo_datestring) }}",
                "person": "{{ dict(uuid=employee_uuid or NONE) }}",
            },
        },
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "__export_to_ldap__": True,
                "givenName": "{{mo_employee.givenname}}",
                "sn": "{{mo_employee.surname}}",
                "displayName": "{{mo_employee.surname}}, {{mo_employee.givenname}}",
                "name": "{{mo_employee.givenname}} {{mo_employee.surname}}",
                "dn": "",
                "employeeID": "{{mo_employee.cpr_no or None}}",
            },
            "Email": {
                "objectClass": "user",
                "__export_to_ldap__": True,
                "employeeID": "{{mo_employee.cpr_no or None}}",
            },
            "Active Directory": {
                "objectClass": "user",
                "__export_to_ldap__": True,
                "msSFU30Name": "{{mo_employee_it_user.user_key}}",
                "employeeID": "{{mo_employee.cpr_no}}",
            },
        },
    }

    settings_mock = MagicMock()
    settings_mock.ldap_search_base = "bar"
    settings_mock.default_org_unit_type = "Afdeling"
    settings_mock.default_org_unit_level = "N1"
    settings_mock.org_unit_path_string_separator = "\\"

    dataloader = MagicMock()
    mo_address_types = {
        "uuid1": {"uuid": "uuid1", "scope": "MAIL", "user_key": "Email"},
        "uuid2": {"uuid": "uuid2", "scope": "TEXT", "user_key": "Post"},
    }
    ad_uuid = str(uuid4())
    mo_it_systems = {
        ad_uuid: {"uuid": ad_uuid, "user_key": "Active Directory"},
    }

    load_mo_address_types = MagicMock()
    load_mo_it_systems = MagicMock()

    load_mo_address_types.return_value = mo_address_types
    load_mo_it_systems.return_value = mo_it_systems

    dataloader.load_mo_address_types = load_mo_address_types
    dataloader.load_mo_it_systems = load_mo_it_systems

    dataloader.upload_mo_objects = AsyncMock()
    dataloader.single_value = {
        "givenName": True,
        "sn": True,
        "displayName": True,
        "name": True,
        "dn": True,
        "employeeID": True,
        "postalAddress": False,
        "mail": True,
        "msSFU30Name": True,
        "itSystemName": True,
    }

    attribute_dict = {
        a: {"single_value": dataloader.single_value[a]}
        for a in dataloader.single_value.keys()
    }

    overview = {"user": {"attributes": attribute_dict}}

    dataloader.load_ldap_overview.return_value = overview
    org_unit_type_uuid = uuid4()
    org_unit_level_uuid = uuid4()
    dataloader.load_mo_org_unit_types.return_value = {
        org_unit_type_uuid: {"uuid": org_unit_type_uuid, "user_key": "Afdeling"}
    }
    dataloader.load_mo_org_unit_levels.return_value = {
        org_unit_level_uuid: {"uuid": org_unit_level_uuid, "user_key": "N1"}
    }

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
            employeeID="0101011234",
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

    mail = converter.from_ldap(
        LdapObject(
            dn="",
            mail=[],
            mail_validity_from=datetime.datetime(2019, 1, 1, 0, 10, 0),
        ),
        "Email",
        employee_uuid=employee_uuid,
    )

    assert not mail


def test_ldap_to_mo_uuid_not_found(context: Context) -> None:
    converter = LdapConverter(context)
    it_users_with_typo = converter.from_ldap(
        LdapObject(
            dn="",
            msSFU30Name=["foo", "bar"],
            itSystemName=["Active Directory", "Active Directory_typo"],
        ),
        "Active Directory",
        employee_uuid=uuid4(),
    )

    it_users = converter.from_ldap(
        LdapObject(
            dn="",
            msSFU30Name=["foo", "bar"],
            itSystemName=["Active Directory", "Active Directory"],
        ),
        "Active Directory",
        employee_uuid=uuid4(),
    )

    assert it_users[0].user_key == "foo"
    assert it_users[1].user_key == "bar"
    ad_uuid = converter.get_it_system_uuid("Active Directory")
    assert str(it_users[0].itsystem.uuid) == ad_uuid
    assert str(it_users[1].itsystem.uuid) == ad_uuid

    # Only one it user should be converted. The second one cannot be found because
    # "Active Directory_typo" does not exist as an it system in MO
    assert len(it_users_with_typo) == 1
    assert len(it_users) == 2


def test_ldap_to_mo_dict_error(context: Context) -> None:

    converter = LdapConverter(context)
    converter.mapping = converter._populate_mapping_with_templates(
        {
            "ldap_to_mo": {
                "Active Directory": {
                    "objectClass": "ramodels.mo.details.it_system.ITUser",
                    "user_key": "{{ ldap.msSFU30Name or NONE }}",
                    "itsystem": "{ 'hep': 'hey }",  # provokes json error in str_to_dict
                    "person": "{{ dict(uuid=employee_uuid or NONE) }}",
                }
            }
        },
        Environment(undefined=Undefined),
    )

    with pytest.raises(IncorrectMapping):
        converter.from_ldap(
            LdapObject(
                dn="",
                msSFU30Name=["foo", "bar"],
                itSystemName=["Active Directory", "Active Directory"],
            ),
            "Active Directory",
            employee_uuid=uuid4(),
        )


def test_mo_to_ldap(converter: LdapConverter) -> None:
    obj_dict: dict = {"mo_employee": Employee(givenname="Tester", surname="Testersen")}
    ldap_object: Any = converter.to_ldap(obj_dict, "Employee", "CN=foo")
    assert ldap_object.givenName == "Tester"
    assert ldap_object.sn == "Testersen"
    assert ldap_object.name == "Tester Testersen"
    assert ldap_object.dn == "CN=foo"

    with pytest.raises(NotSupportedException):
        obj_dict = {"mo_employee_address": "foo"}
        converter.to_ldap(obj_dict, "Employee", "CN=foo")


def test_mapping_loader() -> None:
    mapping = read_mapping_json(
        os.path.join(os.path.dirname(__file__), "resources", "mapping.json")
    )
    expected = {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "__import_to_mo__": True,
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
                "__export_to_ldap__": True,
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
                employee_uuid=uuid4(),
            )[0]
        with pytest.raises(IncorrectMapping):
            obj_dict = {
                "mo_employee": Employee(givenname="Tester", surname="Testersen")
            }
            converter.to_ldap(obj_dict, "Employee", "CN=foo")


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
    assert LdapConverter.filter_splitfirst("foo,bar,pub", separator=",") == [
        "foo",
        "bar,pub",
    ]


def test_splitlast() -> None:
    assert LdapConverter.filter_splitlast("Test") == ["", "Test"]
    assert LdapConverter.filter_splitlast("Test Testersen") == ["Test", "Testersen"]
    assert LdapConverter.filter_splitlast("Test Testersen med test") == [
        "Test Testersen med",
        "test",
    ]
    assert LdapConverter.filter_splitlast("") == ["", ""]
    assert LdapConverter.filter_splitlast("foo,bar,pub", separator=",") == [
        "foo,bar",
        "pub",
    ]


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
                "__export_to_ldap__": True,
                "employeeID": "{{mo_employee.cpr_no or None}}",
            }
        },
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "__import_to_mo__": True,
                "uuid": "{{ employee_uuid }}",
            }
        },
    }

    # This mapping does not contain the mo_employee.cpr_no field
    bad_mapping = {
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "__export_to_ldap__": True,
                "givenName": "{{mo_employee.givenname}}",
            }
        },
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "__import_to_mo__": True,
                "uuid": "{{ employee_uuid }}",
            }
        },
    }

    # Test both cases
    context["user_context"]["mapping"] = good_mapping
    converter = LdapConverter(context)
    assert converter.cpr_field == "employeeID"

    with patch(
        "mo_ldap_import_export.converters.LdapConverter.check_mapping",
        return_value=None,
    ):
        context["user_context"]["mapping"] = bad_mapping
        converter = LdapConverter(context)
        cpr_field = find_cpr_field(converter.mapping)
        assert cpr_field is None

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
                "__import_to_mo__": True,
                "givenname": "{{ldap.givenName}}",
                "surname": "{{ldap.sn}}",
                "uuid": "{{ employee_uuid }}",
            }
        },
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "user",
                "__export_to_ldap__": True,
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
        employee_uuid=uuid4(),
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

    expected_attributes = [
        a for a in all_attributes if a != "objectClass" and not a.startswith("__")
    ]

    assert attributes == expected_attributes


def test_get_mo_attributes(converter: LdapConverter, context: Context):
    attributes = converter.get_mo_attributes("Employee")

    all_attributes = list(
        context["user_context"]["mapping"]["ldap_to_mo"]["Employee"].keys()
    )

    expected_attributes = [
        a for a in all_attributes if a != "objectClass" and not a.startswith("__")
    ]

    assert attributes == expected_attributes


def test_check_attributes(converter: LdapConverter):
    detected_attributes = ["foo", "bar"]
    accepted_attributes = ["bar"]

    with pytest.raises(IncorrectMapping):
        converter.check_attributes(detected_attributes, accepted_attributes)

    detected_attributes = ["bar", "extensionAttribute14"]
    accepted_attributes = ["bar"]
    converter.check_attributes(detected_attributes, accepted_attributes)


def test_get_accepted_json_keys(converter: LdapConverter):
    output = converter.get_accepted_json_keys()
    assert output == ["Employee", "Engagement", "Email", "Post", "Active Directory"]


def test_nonejoin(converter: LdapConverter):
    output = converter.nonejoin("foo", "bar", None)
    assert output == "foo, bar"


def test_str_to_dict(converter: LdapConverter):
    output = converter.str_to_dict("{'foo':2}")
    assert output == {"foo": 2}

    output = converter.str_to_dict("{'foo':Undefined}")
    assert output == {"foo": None}


def test_filter_mo_datestring(converter: LdapConverter):
    output = converter.filter_mo_datestring(datetime.datetime(2019, 4, 13, 20, 10, 10))
    # Note: Dates are always at midnight in MO
    assert output == "2019-04-13T00:00:00"
    assert converter.filter_mo_datestring([]) is None
    assert converter.filter_mo_datestring("") is None
    assert converter.filter_mo_datestring(None) is None


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
        return_value=["Engagement"],
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.import_mo_object_class",
        return_value=Engagement,
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.get_mo_attributes",
        return_value=["user_key"],
    ):
        with pytest.raises(
            IncorrectMapping,
            match=(
                (
                    "attribute .* is mandatory. "
                    "The following attributes are mandatory: .*primary.*"
                )
            ),
        ):
            converter.check_mo_attributes()


async def test_check_ldap_attributes_single_value_fields(converter: LdapConverter):

    dataloader = MagicMock()
    dataloader.load_ldap_overview.return_value = {
        "user": {"attributes": ["attr1", "attr2", "attr3", "attr4"]}
    }

    mapping = {
        "mo_to_ldap": {
            "Address": {
                "attr1": "{{ mo_employee_address.value }}",
                "cpr_field": "{{ foo }}",
            },
            "AD": {
                "attr1": "{{ mo_employee_it_user.user_key }}",
                "cpr_field": "{{ foo }}",
            },
            "Engagement": {
                "attr1": "{{ mo_employee_engagement.user_key }}",
                "attr2": "{{ mo_employee_engagement.org_unit.uuid }}",
                "attr3": "{{ mo_employee_engagement.engagement_type.uuid }}",
                "attr4": "{{ mo_employee_engagement.job_function.uuid }}",
                "cpr_field": "{{ foo }}",
            },
        },
        "ldap_to_mo": {
            "Address": {"value": "ldap.value"},
            "AD": {"user_key": "ldap.user_key"},
            "Engagement": {
                "user_key": "ldap.user_key",
                "org_unit": "ldap.org_unit",
                "engagement_type": "ldap.engagement_type",
                "job_function": "ldap.job_function",
            },
        },
    }
    converter.raw_mapping = mapping.copy()
    converter.mapping = mapping.copy()
    converter.mo_address_types = ["Address"]
    converter.mo_it_systems = ["AD"]

    with patch(
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

            dataloader.single_value = {
                "attr1": True,
                "cpr_field": False,
                "attr2": True,
                "attr3": True,
                "attr4": True,
            }
            converter.dataloader = dataloader

            converter.check_ldap_attributes()

            warnings = [w for w in cap_logs if w["log_level"] == "warning"]
            assert len(warnings) == 6
            for warning in warnings:
                assert re.match(
                    ".*LDAP attribute cannot contain multiple values.*",
                    warning["event"],
                )
        with pytest.raises(IncorrectMapping, match="LDAP Attributes .* are a mix"):
            dataloader.single_value = {
                "attr1": True,
                "cpr_field": False,
                "attr2": True,
                "attr3": True,
                "attr4": False,
            }
            converter.dataloader = dataloader

            converter.check_ldap_attributes()

        with pytest.raises(IncorrectMapping, match="Could not find all attributes"):

            mapping = {
                "mo_to_ldap": {
                    "Engagement": {
                        "attr1": "{{ mo_employee_engagement.user_key }}",
                        "attr2": "{{ mo_employee_engagement.org_unit.uuid }}",
                        "attr3": "{{ mo_employee_engagement.engagement_type.uuid }}",
                        "cpr_field": "{{ foo }}",
                    },
                },
                "ldap_to_mo": {
                    "Engagement": {
                        "user_key": "ldap.user_key",
                        "org_unit": "ldap.org_unit",
                        "engagement_type": "ldap.engagement_type",
                        "job_function": "ldap.job_function",
                    },
                },
            }
            converter.raw_mapping = mapping.copy()
            converter.mapping = mapping.copy()
            converter.check_ldap_attributes()


async def test_check_ldap_attributes_fields_to_check(converter: LdapConverter):

    dataloader = MagicMock()
    dataloader.load_ldap_overview.return_value = {
        "user": {"attributes": ["attr1", "attr2", "attr3", "attr4"]}
    }

    with patch(
        "mo_ldap_import_export.converters.find_cpr_field",
        return_value="cpr_field",
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.check_attributes",
        return_value=None,
    ), patch(
        "mo_ldap_import_export.converters.LdapConverter.find_ldap_object_class",
        return_value="user",
    ):

        dataloader.single_value = {
            "attr1": True,
            "cpr_field": True,
            "attr2": True,
            "attr3": True,
            "attr4": True,
        }
        converter.dataloader = dataloader

        # This mapping is not allowed - because mo_employee_engagement.org_unit.uuid is
        # not in the mo_to_ldap templates
        with pytest.raises(IncorrectMapping):
            mapping = {
                "ldap_to_mo": {
                    "Engagement": {
                        "user_key": "ldap.user_key",
                        "org_unit": "ldap.org_unit",
                        "engagement_type": "ldap.engagement_type",
                        "job_function": "ldap.job_function",
                    },
                },
                "mo_to_ldap": {
                    "Engagement": {
                        "attr1": "{{ mo_employee_engagement.user_key }}",
                        # "attr2": "{{ mo_employee_engagement.org_unit.uuid }}",
                        "attr3": "{{ mo_employee_engagement.engagement_type.uuid }}",
                        "attr4": "{{ mo_employee_engagement.job_function.uuid }}",
                        "cpr_field": "{{ foo }}",
                    },
                },
            }
            converter.raw_mapping = mapping.copy()
            converter.mapping = mapping.copy()
            converter.check_ldap_attributes()

        # This mapping is OK. mo_employee_engagement.org_unit.uuid no longer needs to be
        # in the mo_to_ldap templates. Because the value does not come from LDAP in the
        # first place.
        mapping = {
            "ldap_to_mo": {
                "Engagement": {
                    "user_key": "ldap.user_key",
                    "org_unit": "fixed org unit",
                    "engagement_type": "ldap.engagement_type",
                    "job_function": "ldap.job_function",
                },
            },
            "mo_to_ldap": {
                "Engagement": {
                    "attr1": "{{ mo_employee_engagement.user_key }}",
                    # "attr2": "{{ mo_employee_engagement.org_unit.uuid }}",
                    "attr3": "{{ mo_employee_engagement.engagement_type.uuid }}",
                    "attr4": "{{ mo_employee_engagement.job_function.uuid }}",
                    "cpr_field": "{{ foo }}",
                },
            },
        }
        converter.raw_mapping = mapping.copy()
        converter.mapping = mapping.copy()
        converter.check_ldap_attributes()


async def test_check_dar_scope(converter: LdapConverter):

    address_type_info = {
        "uuid1": {"scope": "TEXT", "user_key": "foo", "uuid": "uuid1"},
        "uuid2": {"scope": "DAR", "user_key": "bar", "uuid": "uuid2"},
    }
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

    address_type_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "foo"},
        "uuid2": {"uuid": "uuid2", "user_key": "bar"},
    }
    converter.address_type_info = address_type_info

    assert converter.get_address_type_uuid("foo") == "uuid1"
    assert converter.get_address_type_uuid("bar") == "uuid2"


async def test_get_it_system_uuid(converter: LdapConverter):
    it_system_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "AD"},
        "uuid2": {"uuid": "uuid2", "user_key": "Office365"},
    }
    converter.it_system_info = it_system_info

    assert converter.get_it_system_uuid("AD") == "uuid1"
    assert converter.get_it_system_uuid("Office365") == "uuid2"


async def test_get_job_function_uuid(converter: LdapConverter):
    job_function_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "Major"},
        "uuid2": {"uuid": "uuid2", "user_key": "Secretary"},
    }
    converter.job_function_info = job_function_info

    assert converter.get_job_function_uuid("Major") == "uuid1"
    assert converter.get_job_function_uuid("Secretary") == "uuid2"


async def test_get_engagement_type_uuid(converter: LdapConverter):
    engagement_type_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "Ansat"},
        "uuid2": {"uuid": "uuid2", "user_key": "Vikar"},
    }
    converter.engagement_type_info = engagement_type_info

    assert converter.get_engagement_type_uuid("Ansat") == "uuid1"
    assert converter.get_engagement_type_uuid("Vikar") == "uuid2"


async def test_get_primary_type_uuid(converter: LdapConverter):
    primary_type_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "primary"},
        "uuid2": {"uuid": "uuid2", "user_key": "non-primary"},
    }
    converter.primary_type_info = primary_type_info

    assert converter.get_primary_type_uuid("primary") == "uuid1"
    assert converter.get_primary_type_uuid("non-primary") == "uuid2"


def test_get_it_system_user_key(converter: LdapConverter):
    it_system_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "AD"},
        "uuid2": {"uuid": "uuid2", "user_key": "Office365"},
    }
    converter.it_system_info = it_system_info

    assert converter.get_it_system_user_key("uuid1") == "AD"
    assert converter.get_it_system_user_key("uuid2") == "Office365"


def test_get_address_type_user_key(converter: LdapConverter):
    address_type_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "EmailUnit"},
        "uuid2": {"uuid": "uuid2", "user_key": "EmailEmployee"},
    }
    converter.address_type_info = address_type_info

    assert converter.get_address_type_user_key("uuid1") == "EmailUnit"
    assert converter.get_address_type_user_key("uuid2") == "EmailEmployee"


def test_get_engagement_type_user_key(converter: LdapConverter):
    engagement_type_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "Ansat"},
        "uuid2": {"uuid": "uuid2", "user_key": "Vikar"},
    }
    converter.engagement_type_info = engagement_type_info

    assert converter.get_engagement_type_user_key("uuid1") == "Ansat"
    assert converter.get_engagement_type_user_key("uuid2") == "Vikar"


def test_get_job_function_user_key(converter: LdapConverter):
    job_function_info = {
        "uuid1": {"uuid": "uuid1", "user_key": "Major"},
        "uuid2": {"uuid": "uuid2", "user_key": "Secretary"},
    }
    converter.job_function_info = job_function_info

    assert converter.get_job_function_user_key("uuid1") == "Major"
    assert converter.get_job_function_user_key("uuid2") == "Secretary"


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


def test_get_object_uuid_from_user_key(converter: LdapConverter):

    uuid = uuid4()
    name = "Skt. Joseph Skole"
    info_dict = {uuid: {"uuid": uuid, "user_key": name}}
    assert converter.get_object_uuid_from_user_key(info_dict, name) == uuid

    with pytest.raises(UUIDNotFoundException):
        info_dict = {uuid: {"uuid": uuid, "user_key": name}}
        converter.get_object_uuid_from_user_key(info_dict, "bar")

    with pytest.raises(UUIDNotFoundException):
        converter.get_object_uuid_from_user_key(info_dict, "")

    uuid2 = uuid4()
    # Check that a perfect match will be preferred over a normalized match
    info_dict = {
        uuid2: {"uuid": uuid2, "user_key": name.lower()},
        uuid: {"uuid": uuid, "user_key": name},
    }
    assert converter.get_object_uuid_from_user_key(info_dict, name) == uuid

    # Check that if no perfect matches exist, use the first match
    info_dict = {
        uuid: {"uuid": uuid, "user_key": name.upper()},
        uuid2: {"uuid": uuid2, "user_key": name.lower()},
    }
    assert converter.get_object_uuid_from_user_key(info_dict, name) == uuid


def test_create_org_unit(converter: LdapConverter):
    uuids = [str(uuid4()), str(uuid4()), str(uuid4())]
    org_units = ["Magenta Aps", "Magenta Aarhus", "GrønlandsTeam"]
    org_unit_infos = [
        {"name": org_units[i], "uuid": uuids[i]} for i in range(len(uuids))
    ]

    converter.org_unit_info = {
        uuids[0]: {**org_unit_infos[0], "parent": None},
        uuids[1]: {**org_unit_infos[1], "parent": org_unit_infos[0]},
        # uuids[2]: {**org_unit_infos[2],"parent":org_unit_infos[1]},
    }

    org_unit_path_string = converter.org_unit_path_string_separator.join(org_units)
    org_units = [info["name"] for info in converter.org_unit_info.values()]

    assert "Magenta Aps" in org_units
    assert "Magenta Aarhus" in org_units
    assert "GrønlandsTeam" not in org_units

    # Create a unit with parents
    converter.create_org_unit(org_unit_path_string)

    org_units = [info["name"] for info in converter.org_unit_info.values()]
    assert "GrønlandsTeam" in org_units

    # Try to create a unit without parents
    converter.create_org_unit("Ørsted")
    org_units = [info["name"] for info in converter.org_unit_info.values()]
    assert "Ørsted" in org_units


def test_get_or_create_org_unit_uuid(converter: LdapConverter):

    uuid = str(uuid4())
    converter.org_unit_info = {
        uuid: {"name": "Magenta Aps", "uuid": uuid, "parent": None}
    }

    # Get an organization UUID
    assert converter.get_or_create_org_unit_uuid("Magenta Aps") == uuid

    # Create a new organization and return its UUID
    converter.get_or_create_org_unit_uuid("Magenta Aarhus")
    org_units = [info["name"] for info in converter.org_unit_info.values()]
    assert "Magenta Aarhus" in org_units

    with pytest.raises(UUIDNotFoundException):
        converter.get_or_create_org_unit_uuid("")


def test_check_info_dict_for_duplicates(converter: LdapConverter):

    info_dict_with_duplicates = {
        uuid4(): {"user_key": "foo"},
        uuid4(): {"user_key": "foo"},
    }

    with pytest.raises(InvalidNameException):
        converter.check_info_dict_for_duplicates(info_dict_with_duplicates)


def test_check_org_unit_info_dict(converter: LdapConverter):

    # This name is invalid because it contains backslashes;
    # Because the org unit path separator is also a backslash.
    converter.org_unit_info = {uuid4(): {"name": "invalid\\name"}}
    with pytest.raises(InvalidNameException):
        converter.check_org_unit_info_dict()


def test_filter_parse_datetime(converter: LdapConverter):
    date = converter.filter_parse_datetime("2021-01-01")
    assert date.strftime("%Y-%m-%d") == "2021-01-01"

    assert converter.filter_parse_datetime("9999-12-31") == pd.Timestamp.max
    assert converter.filter_parse_datetime("200-12-31") == pd.Timestamp.min
    assert converter.filter_parse_datetime("") is None
    assert converter.filter_parse_datetime("None") is None
    assert converter.filter_parse_datetime("NONE") is None
    assert converter.filter_parse_datetime([]) is None
    assert converter.filter_parse_datetime(None) is None


def test_check_uuid_refs_in_mo_objects(converter: LdapConverter):

    with pytest.raises(
        IncorrectMapping, match="Either 'person' or 'org_unit' key needs to be present"
    ):
        converter.raw_mapping = converter.mapping = {
            "ldap_to_mo": {
                "EmailEmployee": {
                    "objectClass": "ramodels.mo.details.address.Address",
                }
            }
        }
        converter.check_uuid_refs_in_mo_objects()

    with pytest.raises(
        IncorrectMapping,
        match="Either 'person' or 'org_unit' key needs to be present.*Not both",
    ):
        converter.raw_mapping = converter.mapping = {
            "ldap_to_mo": {
                "EmailEmployee": {
                    "objectClass": "ramodels.mo.details.address.Address",
                    "person": "{{ dict(uuid=employee_uuid or NONE) }}",
                    "org_unit": "{{ dict(uuid=employee_uuid or NONE) }}",
                }
            }
        }
        converter.check_uuid_refs_in_mo_objects()

    with pytest.raises(
        IncorrectMapping, match="needs to be a dict with 'uuid' as one of it's keys"
    ):
        converter.raw_mapping = converter.mapping = {
            "ldap_to_mo": {
                "EmailEmployee": {
                    "objectClass": "ramodels.mo.details.address.Address",
                    "person": "{{ employee_uuid }}",
                }
            }
        }
        converter.check_uuid_refs_in_mo_objects()

    with pytest.raises(IncorrectMapping, match="needs to contain a key called 'uuid'"):
        converter.raw_mapping = converter.mapping = {
            "ldap_to_mo": {
                "Employee": {
                    "objectClass": "ramodels.mo.employee.Employee",
                }
            }
        }
        converter.check_uuid_refs_in_mo_objects()

    with pytest.raises(
        IncorrectMapping, match="needs to contain a reference to 'employee_uuid'"
    ):
        converter.raw_mapping = converter.mapping = {
            "ldap_to_mo": {
                "Employee": {
                    "objectClass": "ramodels.mo.employee.Employee",
                    "uuid": "{{ uuid4() }}",
                }
            }
        }
        converter.check_uuid_refs_in_mo_objects()


def test_check_get_uuid_functions(converter: LdapConverter):
    converter.check_get_uuid_functions()

    converter.raw_mapping = converter.mapping = {
        "ldap_to_mo": {
            "Email": {
                "address_type": "{{ dict(uuid=get_address_type_uuid('Email')) }}",
            }
        }
    }
    converter.check_get_uuid_functions()

    with pytest.raises(IncorrectMapping):
        converter.raw_mapping = converter.mapping = {
            "ldap_to_mo": {
                "Email": {
                    "address_type": "{{ dict(uuid=get_address_type_uuid('typo')) }}",
                }
            }
        }
        converter.check_get_uuid_functions()


def test__import_to_mo__and__export_to_ldap__(converter: LdapConverter):

    converter.raw_mapping = {
        "mo_to_ldap": {
            "Employee": {"__export_to_ldap__": True},
            "OrgUnit": {"__export_to_ldap__": False},
        },
        "ldap_to_mo": {
            "Employee": {"__import_to_mo__": False},
            "OrgUnit": {"__import_to_mo__": True},
        },
    }

    assert converter.__import_to_mo__("Employee") is False
    assert converter.__import_to_mo__("OrgUnit") is True
    assert converter.__export_to_ldap__("Employee") is True
    assert converter.__export_to_ldap__("OrgUnit") is False


def test_check_import_and_export_flags(converter: LdapConverter):
    converter.raw_mapping = converter.mapping = {
        "mo_to_ldap": {
            "Employee": {"__export_to_ldap__": "True"},
        },
        "ldap_to_mo": {
            "Employee": {"__import_to_mo__": False},
        },
    }

    with pytest.raises(IncorrectMapping, match="not a boolean"):
        converter.check_import_and_export_flags()

    converter.raw_mapping = converter.mapping = {
        "mo_to_ldap": {
            "Employee": {"__export_to_ldap__": True},
        },
        "ldap_to_mo": {
            "Employee": {},
        },
    }

    with pytest.raises(IncorrectMapping, match="Missing '__import_to_mo__' key"):
        converter.check_import_and_export_flags()

    converter.raw_mapping = converter.mapping = {
        "mo_to_ldap": {
            "Employee": {},
        },
        "ldap_to_mo": {
            "Employee": {"__import_to_mo__": True},
        },
    }

    with pytest.raises(IncorrectMapping, match="Missing '__export_to_ldap__' key"):
        converter.check_import_and_export_flags()


def test_find_ldap_it_system():
    environment = Environment()
    template_str = "{{ ldap.distinguishedName }}"
    template = environment.from_string(template_str)

    mapping = {"ldap_to_mo": {"AD": {"user_key": template}}}
    mo_it_systems = ["AD"]
    assert find_ldap_it_system(mapping, mo_it_systems) == "AD"

    mapping = {"ldap_to_mo": {"Wrong AD user_key": {"user_key": template}}}
    mo_it_systems = ["AD"]
    assert find_ldap_it_system(mapping, mo_it_systems) is None

    mapping = {"ldap_to_mo": {"AD": {"user_key": template}}}
    mo_it_systems = []
    assert find_ldap_it_system(mapping, mo_it_systems) is None


def test_check_cpr_field_or_it_system(converter: LdapConverter):

    with patch(
        "mo_ldap_import_export.converters.find_cpr_field",
        return_value=None,
    ), patch(
        "mo_ldap_import_export.converters.find_ldap_it_system",
        return_value=None,
    ):
        with pytest.raises(
            IncorrectMapping,
            match="Neither a cpr-field or an ldap it-system could be found",
        ):
            converter.check_cpr_field_or_it_system()
