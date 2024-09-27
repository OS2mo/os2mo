# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from ldap3 import Connection

from mo_ldap_import_export.ldap import ldap_add
from mo_ldap_import_export.utils import combine_dn_strings


@pytest.fixture
def ldap_suffix() -> list[str]:
    return ["dc=magenta", "dc=dk"]


@pytest.fixture
async def ldap_org(ldap_connection: Connection, ldap_suffix: list[str]) -> list[str]:
    o_dn = ["o=magenta"] + ldap_suffix
    await ldap_add(
        ldap_connection,
        combine_dn_strings(o_dn),
        object_class=["top", "organization"],
        attributes={"objectClass": ["top", "organization"], "o": "magenta"},
    )
    ou_dn = ["ou=os2mo"] + o_dn
    await ldap_add(
        ldap_connection,
        combine_dn_strings(ou_dn),
        object_class=["top", "organizationalUnit"],
        attributes={"objectClass": ["top", "organizationalUnit"], "ou": "os2mo"},
    )
    return ou_dn


@pytest.fixture
async def ldap_person(ldap_connection: Connection, ldap_org: list[str]) -> list[str]:
    person_dn = ["uid=abk"] + ldap_org
    await ldap_add(
        ldap_connection,
        combine_dn_strings(person_dn),
        object_class=["top", "person", "organizationalPerson", "inetOrgPerson"],
        attributes={
            "objectClass": ["top", "person", "organizationalPerson", "inetOrgPerson"],
            "uid": "abk",
            "cn": "Aage Bach Klarskov",
            "givenName": "Aage",
            "sn": "Bach Klarskov",
            "ou": "os2mo",
            "mail": "abk@ad.kolding.dk",
            "userPassword": "{SSHA}j3lBh1Seqe4rqF1+NuWmjhvtAni1JC5A",
            "employeeNumber": "2108613133",
            "title": "Skole underviser",
        },
    )
    return person_dn
