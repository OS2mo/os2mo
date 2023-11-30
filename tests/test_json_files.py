# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
import os
from collections.abc import AsyncIterator
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from contextlib import asynccontextmanager
from typing import Any
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

from .conftest import read_mapping
from mo_ldap_import_export.converters import LdapConverter
from mo_ldap_import_export.customer_specific import JobTitleFromADToMO


@pytest.fixture
def uuid() -> UUID:
    """
    use the same UUID everywhere for easy comparison between converted objects
    """
    return UUID("3f090b29-46b2-4ec4-898f-af244d47dcd4")


json_filenames = [
    f
    for f in os.listdir(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "mo_ldap_import_export",
            "mappings",
        )
    )
    if f.lower().endswith(".yaml")
]

GetConverter = Callable[[str], AbstractAsyncContextManager[LdapConverter]]


@pytest.fixture
async def get_converter(
    settings: MagicMock,
    dataloader: MagicMock,
    username_generator: MagicMock,
    uuid: UUID,
) -> GetConverter:
    """
    dictionary where each key is the json filename and value is the
    corresponding converter
    """

    @asynccontextmanager
    async def converter(json_filename: str) -> AsyncIterator[LdapConverter]:
        org_unit_path_string = "org/unit/path"
        if "holstebro" in json_filename:
            org_unit_path_string = "Holstebro/org/unit/path"

        def get_org_unit_uuid_from_path_mock(org_unit_string):
            if org_unit_string == org_unit_path_string:
                return str(uuid)
            else:
                print("EER", json_filename, org_unit_path_string)
                raise Exception(
                    f"Attempting to find org-unit uuid for '{org_unit_string}'. "
                    f"But expecting '{org_unit_path_string}'"
                )

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
            return_value=org_unit_path_string,
        ):
            converter = LdapConverter(context)
            await converter._init()
            converter.org_unit_path_string_separator = "/"

            # Mock basic functions used by our jinja templates
            converter.get_org_unit_uuid_from_path = AsyncMock(  # type: ignore
                side_effect=get_org_unit_uuid_from_path_mock
            )

            converter.get_object_uuid_from_user_key = MagicMock()  # type: ignore
            converter.get_object_uuid_from_user_key.return_value = str(uuid)

            converter.get_object_uuid_from_name = MagicMock()  # type: ignore
            converter.get_object_uuid_from_name.return_value = str(uuid)

            converter.get_object_user_key_from_uuid = AsyncMock()  # type: ignore
            converter.get_object_user_key_from_uuid.return_value = "object_user_key"

            converter.get_object_name_from_uuid = AsyncMock()  # type: ignore
            converter.get_object_name_from_uuid.return_value = "object_name"

            converter.get_current_engagement_attribute_uuid_dict = (  # type: ignore
                AsyncMock()
            )
            converter.get_current_engagement_attribute_uuid_dict.return_value = {
                "uuid": str(uuid)
            }

            yield converter

    return converter


@pytest.mark.parametrize("json_filename", json_filenames)
async def test_back_and_forth_mapping(
    get_converter: GetConverter, uuid: UUID, json_filename: str
):
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

    mo_jobtilte_cust = JobTitleFromADToMO.from_simplified_fields(
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
        "mo_jobtilte_cust": mo_jobtilte_cust,
    }

    dn = "CN=Bill Cosby,OU=foo,DC=US_of_A"

    async with get_converter(json_filename) as converter:
        print("-" * 40)
        print(f"Testing '{json_filename}' mapping")
        print("-" * 40)

        engagement_uuid: UUID = uuid4()
        json_keys = converter.get_json_keys("ldap_to_mo")
        raw_mapping = converter.raw_mapping

        for json_key in json_keys:
            print(f"Testing '{json_key}' json_key")

            ldap_object = await converter.to_ldap(mo_object_dict, json_key, dn)
            converted_mo_object = (
                await converter.from_ldap(
                    ldap_object, json_key, uuid, engagement_uuid=engagement_uuid
                )
            )[0]

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


async def convert_address_to_ldap(address, json_key, converter):
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

    return await converter.to_ldap(mo_object_dict, json_key, "CN=foo")


async def test_alleroed_employee_mapping(get_converter: GetConverter):
    """
    Test that givenname, surname, nickname and so on get combined and split properly.
    """
    async with get_converter("alleroed.yaml") as converter:
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

        ldap_employee = await converter.to_ldap(mo_object_dict, "Employee", "CN=foo")

        assert ldap_employee.givenName == "Lukas"  # type: ignore
        assert ldap_employee.sn == "Skywalker"  # type: ignore
        assert ldap_employee.displayName == "Lucky Luke"  # type: ignore

        mo_employee_converted = (
            await converter.from_ldap(ldap_employee, "Employee", mo_employee.uuid)
        )[0]

        assert mo_employee_converted == mo_employee


@pytest.mark.parametrize("json_filename", json_filenames)
async def test_objectguid_mappings(get_converter: GetConverter, json_filename: str):
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

    async with get_converter(json_filename) as converter:
        json_keys = converter.get_json_keys("mo_to_ldap")
        for json_key in json_keys:
            attributes = converter.get_ldap_attributes(json_key)

            for attribute in attributes:
                if attribute.lower() == "objectguid":
                    ldap_object = await converter.to_ldap(
                        mo_object_dict, json_key, "CN=foo"
                    )

                    objectGUID = getattr(ldap_object, attribute)
                    assert UUID(objectGUID)
                    assert objectGUID.startswith("{")
                    assert objectGUID.endswith("}")
