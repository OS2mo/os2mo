# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import pytest

from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.types import RDN
from mo_ldap_import_export.utils import combine_dn_strings


@pytest.mark.integration_test
@pytest.mark.usefixtures("test_client")
@pytest.mark.parametrize(
    "idn,rdn",
    [
        # Update RDN with similar RDN
        ("uid=abk", "uid=2108613133"),
        ("cn=Aage Bach Klarskov", "cn=Morris Bach"),
        # Update RDN with different RDN
        ("uid=abk", "cn=Aage Bach Klarskov"),
        ("givenName=Anders", "uid=abk"),
        # Moving from a non-current cn to an uid is okay
        ("cn=Anders", "uid=abk"),
        # However moving from the current cn to an uid fails
        # It fails with an objectClassViolation, because cn is required
        # However in the above test moving from givenName to uid DOES NOT clear
        # givenName, so it seems to be a specific issue with cn???
        # TODO: Figure out what the hell is going on?
        pytest.param(
            "cn=Anders And",
            "uid=abk",
            marks=pytest.mark.xfail(reason="Cannot move from real cn to uid"),
        ),
    ],
)
async def test_ldap_modify_dn(
    ldap_api: LDAPAPI,
    ldap_org_unit: list[str],
    idn: RDN,
    rdn: RDN,
) -> None:
    # This is the DN we start at
    initial_dn = combine_dn_strings([idn] + ldap_org_unit)
    # This is the DN we want to move to
    expected_dn = combine_dn_strings([rdn] + ldap_org_unit)

    await ldap_api.ldap_connection.ldap_add(
        dn=initial_dn,
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={
            "objectClass": ["top", "person", "organizationalPerson", "inetOrgPerson"],
            "ou": "os2mo",
            "cn": "Anders And",
            "sn": "And",
            "givenName": "Anders",
        },
    )
    initial_ldap_uuid = await ldap_api.get_ldap_unique_ldap_uuid(initial_dn)

    await ldap_api.ldap_connection.ldap_modify_dn(initial_dn, rdn)

    new_dn = await ldap_api.get_ldap_dn(initial_ldap_uuid)
    assert new_dn is not None
    assert new_dn == expected_dn
