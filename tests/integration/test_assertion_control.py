# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from ldap3 import Connection
from ldap3.core.exceptions import LDAPAssertionFailedResult
from more_itertools import one

from mo_ldap_import_export.ldap import construct_assertion_control
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
