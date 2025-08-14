# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import LDAPUUID


@pytest.mark.integration_test
async def test_uuid_to_dn_to_uuid(
    ldap_api: LDAPAPI, ldap_person_uuid: LDAPUUID
) -> None:
    dn = await ldap_api.get_ldap_dn(ldap_person_uuid)
    assert await ldap_api.get_ldap_unique_ldap_uuid(dn) == ldap_person_uuid


@pytest.mark.integration_test
async def test_dn_to_uuid_to_dn(ldap_api: LDAPAPI, ldap_person_dn: DN) -> None:
    uuid = await ldap_api.get_ldap_unique_ldap_uuid(ldap_person_dn)
    assert await ldap_api.get_ldap_dn(uuid) == ldap_person_dn
