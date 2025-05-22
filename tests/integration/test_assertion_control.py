# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import pytest
from ldap3 import Connection
from ldap3.core.exceptions import LDAPAssertionFailedResult
from more_itertools import one

from mo_ldap_import_export.ldap import construct_assertion_control
from mo_ldap_import_export.ldap import construct_assertion_control_filter
from mo_ldap_import_export.ldap import get_ldap_object
from mo_ldap_import_export.ldap import ldap_add
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.utils import combine_dn_strings


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_assertion_controls_allows(
    ldap_connection: Connection,
    ldap_api: LDAPAPI,
    ldap_org_unit: list[str],
) -> None:
    """Test that Assertion Controls can be used and have an operation pass."""
    person_dn = combine_dn_strings(["uid=valdez"] + ldap_org_unit)

    await ldap_add(
        ldap_connection,
        dn=person_dn,
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={"givenName": "Dana", "sn": "Valdez", "cn": "Valdez"},
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName")
    assert one(result.givenName) == "Dana"

    search_filter = "(sn=Valdez)"
    await ldap_api.ldap_connection.ldap_modify(
        dn=person_dn,
        changes={"givenName": [("MODIFY_REPLACE", "Erika")]},
        controls=[construct_assertion_control(search_filter)],
    )

    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName")
    assert one(result.givenName) == "Erika"


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_assertion_controls_blocks(
    ldap_connection: Connection,
    ldap_api: LDAPAPI,
    ldap_org_unit: list[str],
) -> None:
    """Test that Assertion Controls can be used and have an operation fail."""
    person_dn = combine_dn_strings(["uid=valdez"] + ldap_org_unit)

    await ldap_add(
        ldap_connection,
        dn=person_dn,
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={"givenName": "Dana", "sn": "Valdez", "cn": "Valdez"},
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName")
    assert one(result.givenName) == "Dana"

    search_filter = "(sn=Anchorage)"
    with pytest.raises(LDAPAssertionFailedResult) as exc_info:
        await ldap_api.ldap_connection.ldap_modify(
            dn=person_dn,
            changes={"givenName": [("MODIFY_REPLACE", "Erika")]},
            controls=[construct_assertion_control(search_filter)],
        )
    assert "LDAPAssertionFailedResult - 122 - assertionFailed" in str(exc_info.value)

    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName")
    assert one(result.givenName) == "Dana"


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_assertion_controls_empty(
    ldap_connection: Connection,
    ldap_api: LDAPAPI,
    ldap_org_unit: list[str],
) -> None:
    """Test that Assertion Controls can be used and have an operation pass."""
    person_dn = combine_dn_strings(["uid=valdez"] + ldap_org_unit)

    await ldap_add(
        ldap_connection,
        dn=person_dn,
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={"sn": "Valdez", "cn": "Valdez"},
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName") is False

    # Construct Assertion Control filter checking that givenName is empty
    search_filter = construct_assertion_control_filter({"givenName": []})
    assertion_control = construct_assertion_control(search_filter)

    # Add givenName, should pass because givenName is unset
    await ldap_api.ldap_connection.ldap_modify(
        dn=person_dn,
        changes={"givenName": [("MODIFY_REPLACE", "Dana")]},
        controls=[assertion_control],
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName")
    assert one(result.givenName) == "Dana"

    # Edit givenName, should fail because givenName is 'Dana'
    with pytest.raises(LDAPAssertionFailedResult) as exc_info:
        await ldap_api.ldap_connection.ldap_modify(
            dn=person_dn,
            changes={"givenName": [("MODIFY_REPLACE", "Erika")]},
            controls=[assertion_control],
        )
    assert "LDAPAssertionFailedResult - 122 - assertionFailed" in str(exc_info.value)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_assertion_controls_multivalued(
    ldap_connection: Connection,
    ldap_api: LDAPAPI,
    ldap_org_unit: list[str],
) -> None:
    """Test that Assertion Controls can be used and have an operation pass."""
    person_dn = combine_dn_strings(["uid=valdez"] + ldap_org_unit)

    await ldap_add(
        ldap_connection,
        dn=person_dn,
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={"sn": "Valdez", "cn": ["Valdez", "Koi"]},
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "cn")
    assert result.cn == ["Valdez", "Koi"]

    # Construct Assertion Control filter checking that givenName is empty
    search_filter = construct_assertion_control_filter({"cn": ["Valdez", "Koi"]})
    assertion_control = construct_assertion_control(search_filter)

    # Modify common name, should pass because both common names are set
    await ldap_api.ldap_connection.ldap_modify(
        dn=person_dn,
        changes={"cn": [("MODIFY_REPLACE", "Valdez")]},
        controls=[assertion_control],
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "cn")
    assert one(result.cn) == "Valdez"

    # Modify common name, should fail because only one common name is set
    with pytest.raises(LDAPAssertionFailedResult) as exc_info:
        await ldap_api.ldap_connection.ldap_modify(
            dn=person_dn,
            changes={"cn": [("MODIFY_REPLACE", "Koi")]},
            controls=[assertion_control],
        )
    assert "LDAPAssertionFailedResult - 122 - assertionFailed" in str(exc_info.value)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_assertion_controls_spaces(
    ldap_connection: Connection,
    ldap_api: LDAPAPI,
    ldap_org_unit: list[str],
) -> None:
    """Test that Assertion Controls can be used and have an operation pass."""
    person_dn = combine_dn_strings(["uid=valdez"] + ldap_org_unit)

    await ldap_add(
        ldap_connection,
        dn=person_dn,
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={"sn": "Valdez", "cn": ["De Valdez"], "carLicense": " "},
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "cn")
    assert result.cn == ["De Valdez"]
    assert hasattr(result, "carLicense")
    assert result.carLicense == [" "]

    # Construct Assertion Control filter checking that givenName is empty
    search_filter = construct_assertion_control_filter(
        {"cn": ["De Valdez"], "carLicense": " "}
    )
    assertion_control = construct_assertion_control(search_filter)

    # Modify carLicense, should pass because carLicense is " " currently
    await ldap_api.ldap_connection.ldap_modify(
        dn=person_dn,
        changes={"carLicense": [("MODIFY_REPLACE", "Renewed")]},
        controls=[assertion_control],
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "cn")
    assert one(result.cn) == "De Valdez"
    assert hasattr(result, "carLicense")
    assert result.carLicense == ["Renewed"]

    # Modify carLicense, should fail because carLicense is "Renewed" currently
    with pytest.raises(LDAPAssertionFailedResult) as exc_info:
        await ldap_api.ldap_connection.ldap_modify(
            dn=person_dn,
            changes={"carLicense": [("MODIFY_REPLACE", " ")]},
            controls=[assertion_control],
        )
    assert "LDAPAssertionFailedResult - 122 - assertionFailed" in str(exc_info.value)


@pytest.mark.parametrize(
    "filter", [{"dn": "CN=foo"}, {"sn": "Valdez", "dn": "CN=foo", "cn": "foo"}]
)
async def test_construct_assertion_control_filter_dn_disallowed(filter) -> None:
    with pytest.raises(ValueError) as exc_info:
        construct_assertion_control_filter(filter)
    assert "Cannot use DN in Assertion Control" in str(exc_info.value)


@pytest.mark.parametrize(
    "filter, expected",
    [
        # No filter
        ({}, "(objectClass=*)"),
        # Single filter
        ({"sn": "Valdez"}, "(sn=Valdez)"),
        ({"sn": ["Valdez"]}, "(sn=Valdez)"),
        # Two filters combined
        ({"sn": "Valdez", "cn": "Dana"}, "(&(sn=Valdez)(cn=Dana))"),
        ({"sn": ["Valdez"], "cn": "Dana"}, "(&(sn=Valdez)(cn=Dana))"),
        ({"sn": "Valdez", "cn": ["Dana"]}, "(&(sn=Valdez)(cn=Dana))"),
        ({"sn": ["Valdez"], "cn": ["Dana"]}, "(&(sn=Valdez)(cn=Dana))"),
        # Three filters combined
        (
            {"sn": "Valdez", "cn": "Dana", "givenName": "Dana"},
            "(&(sn=Valdez)(cn=Dana)(givenName=Dana))",
        ),
        # Unicode
        ({"favorite_emoji": "😊"}, "(favorite_emoji=😊)"),
        # Asterisk (actually searches for asterisk, not wildcard)
        ({"algorithm": "A*"}, r"(algorithm=A\2a)"),
        # Backslash escape character
        ({"homeDrive": r"C:\>"}, r"(homeDrive=C:\5c>)"),
        # Parentheses
        ({"context": "foo()"}, r"(context=foo\28\29)"),
        # Null character
        ({"extensionAttribute1": "\x00"}, r"(extensionAttribute1=\00)"),
        # Torture test
        (
            {"context": "bar(*args, **kwargs) \\ \x00", "sn": "&Valdez"},
            r"(&(context=bar\28\2aargs,\20\2a\2akwargs\29\20\5c\20\00)(sn=&Valdez))",
        ),
        # Empty list
        ({"sn": []}, "(!(sn=*))"),
        ({"sn": [], "cn": []}, "(&(!(sn=*))(!(cn=*)))"),
        # Multielement list
        ({"sn": ["Valdez", "Koi"]}, "(&(sn=Valdez)(sn=Koi))"),
        (
            {"sn": ["Valdez", "Koi"], "cn": ["Dana"]},
            "(&(&(sn=Valdez)(sn=Koi))(cn=Dana))",
        ),
        # Spaces
        ({"sn": "De Valdez"}, r"(sn=De\20Valdez)"),
        ({"sn": " "}, r"(sn=\20)"),
        ({"sn": "  x  "}, r"(sn=\20\20x\20\20)"),
    ],
)
async def test_construct_assertion_control_filter(
    filter: dict[str, Any], expected: str
) -> None:
    assert construct_assertion_control_filter(filter) == expected
