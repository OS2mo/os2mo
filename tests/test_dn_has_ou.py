# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from ldap3.core.exceptions import LDAPInvalidDnError

from mo_ldap_import_export.environments.main import dn_has_ou
from mo_ldap_import_export.types import DN


@pytest.mark.parametrize(
    "dn,expected",
    (
        ("DC=example,DC=local", False),
        ("OU=magenta,DC=example,DC=local", True),
        ("OU=os2mo,OU=magenta,DC=local", True),
        ("OU=os2mo,OU=magenta", True),
        ("CN=atlas,OU=os2mo,OU=magenta", True),
        ("UID=abk,OU=os2mo,OU=magenta", True),
        ("UID=\\ spaces\\ ,OU=\\ in\\ ,OU=\\ values\\ ", True),
        ("A=B,C=D,E=F,G=H", False),
        ("DC=OU,DC=local", False),
        ("DC=ou,DC=local", False),
        ("ou=os2mo,DC=local", True),
    ),
)
async def test_dn_has_ou(dn: DN, expected: bool) -> None:
    assert dn_has_ou(dn) is expected


async def test_dn_has_ou_empty() -> None:
    with pytest.raises(LDAPInvalidDnError) as exc_info:
        dn_has_ou("")
    assert "empty dn" in str(exc_info.value)


@pytest.mark.parametrize(
    "dn",
    (
        "OU=test, SPACE_IN_KEY =hi",
        "OU=test, SPACE_IN_KEY =hi,DC=local",
    ),
)
async def test_dn_has_ou_invalid(dn: DN) -> None:
    with pytest.raises(LDAPInvalidDnError) as exc_info:
        dn_has_ou(dn)
    assert "character ' ' not allowed in attribute type" in str(exc_info.value)
