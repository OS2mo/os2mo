# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from mo_ldap_import_export.exceptions import ReadOnlyException
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.types import DN


@pytest.mark.integration_test
@pytest.mark.envvar({"LDAP_READ_ONLY": "true"})
async def test_modify_ldap_object_read_only(
    ldap_api: LDAPAPI, ldap_person_dn: DN
) -> None:
    with pytest.raises(ReadOnlyException) as exc_info:
        await ldap_api.modify_ldap_object(ldap_person_dn, {"title": ["whatever"]})
    assert "LDAP connection is read-only" in str(exc_info.value)


@pytest.mark.integration_test
@pytest.mark.envvar({"LDAP_READ_ONLY": "true"})
async def test_add_ldap_object_read_only(ldap_api: LDAPAPI, ldap_person_dn: DN) -> None:
    with pytest.raises(ReadOnlyException) as exc_info:
        await ldap_api.add_ldap_object(
            ldap_person_dn, {"title": ["whatever"]}, "inetOrgPerson"
        )
    assert "LDAP connection is read-only" in str(exc_info.value)


@pytest.mark.integration_test
@pytest.mark.envvar({"ADD_OBJECTS_TO_LDAP": "false"})
async def test_add_ldap_object_no_add(ldap_api: LDAPAPI, ldap_person_dn: DN) -> None:
    with pytest.raises(ReadOnlyException) as exc_info:
        await ldap_api.add_ldap_object(
            ldap_person_dn, {"title": ["whatever"]}, "inetOrgPerson"
        )
    assert "Adding LDAP objects is disabled" in str(exc_info.value)
