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
from mo_ldap_import_export.ldap import ldap_modify
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
    await ldap_modify(
        ldap_connection,
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
        await ldap_modify(
            ldap_connection,
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
    await ldap_modify(
        ldap_connection,
        dn=person_dn,
        changes={"givenName": [("MODIFY_REPLACE", "Dana")]},
        controls=[assertion_control],
    )
    result = await get_ldap_object(ldap_connection, person_dn)
    assert hasattr(result, "givenName")
    assert one(result.givenName) == "Dana"

    # Edit givenName, should fail because givenName is 'Dana'
    with pytest.raises(LDAPAssertionFailedResult) as exc_info:
        await ldap_modify(
            ldap_connection,
            dn=person_dn,
            changes={"givenName": [("MODIFY_REPLACE", "Erika")]},
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
        # Two filters combined
        ({"sn": "Valdez", "cn": "Dana"}, "(&(sn=Valdez)(cn=Dana))"),
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
            r"(&(context=bar\28\2aargs, \2a\2akwargs\29 \5c \00)(sn=&Valdez))",
        ),
        # Empty list
        ({"sn": []}, "(!(sn=*))"),
        ({"sn": [], "cn": []}, "(&(!(sn=*))(!(cn=*)))"),
    ],
)
async def test_construct_assertion_control_filter(
    filter: dict[str, Any], expected: str
) -> None:
    assert construct_assertion_control_filter(filter) == expected
