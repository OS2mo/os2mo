# -*- coding: utf-8 -*-
import os
from typing import Any
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

from .conftest import read_mapping
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.customer_specific import HolstebroEngagementUpdate


@pytest.fixture
def uuid() -> UUID:
    """
    use the same UUID everywhere for easy comparison between converted objects
    """
    return UUID("3f090b29-46b2-4ec4-898f-af244d47dcd4")


@pytest.fixture
def json_filenames() -> list[str]:
    """
    Return filenames of all json-formatted mapping files
    """
    return [
        f
        for f in os.listdir(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "mo_ldap_import_export",
                "mappings",
            )
        )
        if f.lower().endswith(".json")
    ]


@pytest.fixture
def converters(
    json_filenames: str,
    settings: MagicMock,
    dataloader: MagicMock,
    username_generator: MagicMock,
    uuid: UUID,
) -> dict[str, LdapConverter]:
    """
    dictionary where each key is the json filename and value is the
    corresponding converter
    """
    converters = {}

    for json_filename in json_filenames:
        user_context = {}
        user_context["mapping"] = read_mapping(json_filename)
        user_context["settings"] = settings
        user_context["dataloader"] = dataloader
        user_context["username_generator"] = username_generator
        user_context["forbidden_usernames_path"] = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "mo_ldap_import_export",
            "mappings",
            "forbidden_usernames",
        )
        context = Context({"user_context": user_context})

        # Patch out mapping checks, most of those require a connection to LDAP/MO
        with patch(
            "mo_ldap_import_export.converters.LdapConverter.check_mapping",
            return_value=None,
        ), patch(
            "mo_ldap_import_export.converters.LdapConverter.check_info_dicts",
            return_value=None,
        ), patch(
            (
                "mo_ldap_import_export.converters.LdapConverter."
                "get_object_uuid_from_user_key"
            ),
            return_value=str(uuid),
        ), patch(
            "mo_ldap_import_export.converters.LdapConverter.get_org_unit_path_string",
            return_value=str("org/unit/path"),
        ):
            converter = LdapConverter(context)

            # Mock basic functions used by our jinja templates
            converter.clean_org_unit_path_string = MagicMock()  # type: ignore
            converter.clean_org_unit_path_string.return_value = "org/unit/path"

            converter.get_org_unit_uuid_from_path = MagicMock()  # type: ignore
            converter.get_org_unit_uuid_from_path.return_value = str(uuid)

            converter.get_object_uuid_from_user_key = MagicMock()  # type: ignore
            converter.get_object_uuid_from_user_key.return_value = str(uuid)

            converter.get_object_uuid_from_name = MagicMock()  # type: ignore
            converter.get_object_uuid_from_name.return_value = str(uuid)

            converter.get_object_user_key_from_uuid = MagicMock()  # type: ignore
            converter.get_object_user_key_from_uuid.return_value = "object_user_key"

            converter.get_object_name_from_uuid = MagicMock()  # type: ignore
            converter.get_object_name_from_uuid.return_value = "object_name"

            converter.get_current_engagement_attribute_uuid_dict = (  # type: ignore
                MagicMock()
            )
            converter.get_current_engagement_attribute_uuid_dict.return_value = {
                "uuid": str(uuid)
            }

            converters[json_filename] = converter

    return converters


def test_init_json_keys_in_mapping(converters: dict[str, LdapConverter]):
    """
    Checks that all classes which are being created on startup are also used in
    the mapping
    """
    for converter in converters.values():
        facet_mapping = converter.mapping.get("init", {}).get("facets", {})
        it_system_mapping = converter.mapping.get("init", {}).get("it_systems", {})

        it_system_json_keys = list(it_system_mapping.keys())

        facet_json_keys = []
        for facet in facet_mapping.values():
            facet_json_keys.extend(list(facet.keys()))

        init_json_keys = facet_json_keys + it_system_json_keys
        mapped_json_keys = converter.get_mo_to_ldap_json_keys()

        for init_json_key in init_json_keys:
            assert init_json_key in mapped_json_keys


def test_address_types(converters: dict[str, LdapConverter]):
    """
    Test that address_type attributes in ldap_to_mo mapping are formatted properly
    """
    for converter in converters.values():
        mapping = converter.raw_mapping

        for key, mapping_dict in mapping["ldap_to_mo"].items():
            object_class = mapping_dict["objectClass"]
            if object_class == "ramodels.mo.details.address.Address":

                if "org_unit" in mapping_dict:
                    address_type_template = (
                        f"{{{{ dict(uuid=get_org_unit_address_type_uuid('{key}')) }}}}"
                    )
                else:
                    address_type_template = (
                        f"{{{{ dict(uuid=get_employee_address_type_uuid('{key}')) }}}}"
                    )
                assert mapping_dict["address_type"] == address_type_template

            elif object_class == "ramodels.mo.details.it_system.ITUser":

                it_system_template = f"{{{{ dict(uuid=get_it_system_uuid('{key}')) }}}}"
                assert mapping_dict["itsystem"] == it_system_template


def test_back_and_forth_mapping(converters: dict[str, LdapConverter], uuid: UUID):

    mo_employee = Employee(
        givenname="Bill",
        surname="Cosby",
        cpr_no="0101011234",
        nickname_givenname="Billy John",
        nickname_surname="Cosplayer",
        user_key="unique_key",
        uuid=uuid,
    )

    mo_employee_address = Address.from_simplified_fields(
        value="Fleet street 30, 1234, London",
        address_type_uuid=uuid,
        from_date="2021-01-01",
        uuid=uuid,
        to_date=None,
        value2="foo",
        person_uuid=uuid,
        org_unit_uuid=None,
        engagement_uuid=None,
        visibility_uuid=uuid,
        org_uuid=None,
    )

    mo_org_unit_address = Address.from_simplified_fields(
        value="Baker street 221B",
        address_type_uuid=uuid,
        from_date="2020-01-01",
        uuid=uuid,
        to_date=None,
        value2="food",
        person_uuid=None,
        org_unit_uuid=uuid,
        engagement_uuid=None,
        visibility_uuid=uuid,
        org_uuid=None,
    )

    mo_employee_it_user = ITUser.from_simplified_fields(
        user_key="my-username",
        itsystem_uuid=uuid,
        from_date="2021-01-01",
        uuid=uuid,
        to_date=None,
        person_uuid=uuid,
        org_unit_uuid=None,
    )

    mo_employee_engagement = Engagement.from_simplified_fields(
        org_unit_uuid=uuid,
        person_uuid=uuid,
        job_function_uuid=uuid,
        engagement_type_uuid=uuid,
        user_key="engagement_ID",
        from_date="2021-01-01",
        to_date=None,
        uuid=uuid,
        primary_uuid=uuid,
        extension_1="1",
        extension_2="2",
        extension_3="3",
        extension_4="4",
        extension_5="5",
        extension_6="6",
        extension_7="7",
        extension_8="8",
        extension_9="9",
        extension_10="10",
    )

    mo_holstebro_cust = HolstebroEngagementUpdate.from_simplified_fields(
        user_uuid=uuid,
        job_function_uuid=uuid,
        job_function_fallback_uuid=uuid,
        title=uuid,
    )

    mo_object_dict = {
        "mo_employee": mo_employee,
        "mo_org_unit_address": mo_org_unit_address,
        "mo_employee_address": mo_employee_address,
        "mo_employee_it_user": mo_employee_it_user,
        "mo_employee_engagement": mo_employee_engagement,
        "mo_holstebro_cust": mo_holstebro_cust,
    }

    for json_file, converter in converters.items():
        print("-" * 40)
        print(f"Testing '{json_file}' mapping")
        print("-" * 40)
        json_keys = converter.get_json_keys("ldap_to_mo")
        raw_mapping = converter.raw_mapping
        for json_key in json_keys:
            print(f"Testing '{json_key}' json_key")

            ldap_object = converter.to_ldap(mo_object_dict, json_key, "CN=foo")
            converted_mo_object = converter.from_ldap(ldap_object, json_key, uuid)[0]

            # Skip validity, because we often set from_date = now()
            attributes_to_skip = ["validity"]
            mo_attributes = converter.get_mo_attributes(json_key)

            for attribute in mo_attributes:
                if attribute in attributes_to_skip:
                    continue
                print(f"Testing '{attribute}' attribute")

                template = raw_mapping["ldap_to_mo"][json_key][attribute]

                # If we hard-code a value, we do not expect a match.
                if "ldap." not in template:
                    continue

                original_values: list[Any] = list(
                    filter(
                        None,
                        [getattr(o, attribute, None) for o in mo_object_dict.values()],
                    )
                )

                assert getattr(converted_mo_object, attribute) in original_values


def convert_address_to_ldap(address, json_key, converter):
    """
    Convert a MO address to ldap
    """
    mo_employee = Employee(cpr_no="0101011234")

    mo_org_unit_address = Address.from_simplified_fields(
        address, uuid4(), "2021-01-01", org_unit_uuid=uuid4()
    )

    mo_object_dict = {
        "mo_employee": mo_employee,
        "mo_org_unit_address": mo_org_unit_address,
    }

    return converter.to_ldap(mo_object_dict, json_key, "CN=foo")


def test_alleroed_employee_mapping(converters: dict[str, LdapConverter]):
    """
    Test that givenname, surname, nickname and so on get combined and split properly.
    """
    converter = converters["alleroed.json"]
    mo_employee = Employee(
        cpr_no="0101011234",
        givenname="Lukas",
        surname="Skywalker",
        nickname_givenname="Lucky",
        nickname_surname="Luke",
    )

    mo_object_dict = {
        "mo_employee": mo_employee,
    }

    ldap_employee = converter.to_ldap(mo_object_dict, "Employee", "CN=foo")

    assert ldap_employee.givenName == "Lukas"  # type: ignore
    assert ldap_employee.sn == "Skywalker"  # type: ignore
    assert ldap_employee.displayName == "Lucky Luke"  # type: ignore

    mo_employee_converted = converter.from_ldap(
        ldap_employee, "Employee", mo_employee.uuid
    )[0]

    assert mo_employee_converted == mo_employee


def test_objectguid_mappings(converters: dict[str, LdapConverter]):
    """
    Validate that objectGUIDs get written to LDAP properly
    """

    mo_employee = Employee(
        cpr_no="0101011234",
    )

    mo_employee_it_user = ITUser.from_simplified_fields(
        user_key=str(uuid4()),
        itsystem_uuid=uuid4(),
        from_date="2021-01-01",
    )

    mo_object_dict = {
        "mo_employee": mo_employee,
        "mo_employee_it_user": mo_employee_it_user,
    }

    for converter in converters.values():
        json_keys = converter.get_json_keys("mo_to_ldap")
        for json_key in json_keys:
            attributes = converter.get_ldap_attributes(json_key)

            for attribute in attributes:
                if attribute.lower() == "objectguid":
                    ldap_object = converter.to_ldap(mo_object_dict, json_key, "CN=foo")

                    objectGUID = getattr(ldap_object, attribute)
                    assert UUID(objectGUID)
                    assert objectGUID.startswith("{")
                    assert objectGUID.endswith("}")


def test_startup_checks_on_all_json_files(converters: dict[str, LdapConverter]):
    """
    Run the startup checks which we can run without being connected to MO or LDAP
    """
    for converter in converters.values():
        converter.cross_check_keys()
        converter.check_for_objectClass()
        converter.check_mo_attributes()
        converter.check_uuid_refs_in_mo_objects()
        converter.check_import_and_export_flags()
