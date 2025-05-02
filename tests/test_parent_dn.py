# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from ldap3.core.exceptions import LDAPInvalidDnError

from mo_ldap_import_export.environments.main import parent_dn
from mo_ldap_import_export.types import DN


@pytest.mark.parametrize(
    "dn,expected",
    (
        ("DC=example,DC=local", "DC=local"),
        ("OU=magenta,DC=example,DC=local", "DC=example,DC=local"),
        ("OU=os2mo,OU=magenta,DC=local", "OU=magenta,DC=local"),
        ("OU=os2mo,OU=magenta", "OU=magenta"),
        ("CN=atlas,OU=os2mo,OU=magenta", "OU=os2mo,OU=magenta"),
        ("UID=abk,OU=os2mo,OU=magenta", "OU=os2mo,OU=magenta"),
        ("UID= spaces ,OU= in ,OU= values ", r"OU=\ in\ ,OU=\ values\ "),
        ("A=B,C=D,E=F,G=H", "C=D,E=F,G=H"),
    ),
)
async def test_parent_dn(dn: DN, expected: DN) -> None:
    assert parent_dn(dn) == expected


@pytest.mark.parametrize(
    "dn",
    (
        "",
        "DC=local",
        "OU=magenta",
        "X=Y",
    ),
)
async def test_parent_dn_empty(dn: DN) -> None:
    with pytest.raises(LDAPInvalidDnError) as exc_info:
        parent_dn(dn)
    assert "empty dn" in str(exc_info.value)


@pytest.mark.parametrize(
    "dn",
    (
        "OU=test, SPACE_IN_KEY =hi",
        "OU=test, SPACE_IN_KEY =hi,DC=local",
    ),
)
async def test_parent_dn_invalid(dn: DN) -> None:
    with pytest.raises(LDAPInvalidDnError) as exc_info:
        parent_dn(dn)
    assert "character ' ' not allowed in attribute type" in str(exc_info.value)
