# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
import datetime
from typing import Any

import pytest
from ldap3.core.exceptions import LDAPInvalidDnError

from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import RDN
from mo_ldap_import_export.utils import combine_dn_strings
from mo_ldap_import_export.utils import extract_ou_from_dn
from mo_ldap_import_export.utils import get_delete_flag
from mo_ldap_import_export.utils import import_class
from mo_ldap_import_export.utils import mo_datestring_to_utc
from mo_ldap_import_export.utils import mo_today
from mo_ldap_import_export.utils import remove_vowels


async def test_import_class() -> None:
    imported_class = import_class("Employee")
    assert imported_class.__name__ == "Employee"

    imported_class = import_class("Custom.JobTitleFromADToMO")
    assert imported_class.__name__ == "JobTitleFromADToMO"

    with pytest.raises(NotImplementedError) as exc_info:
        import_class("Ashbringer")
    assert "Unknown argument to import_class" in str(exc_info.value)


async def test_mo_datestring_to_utc() -> None:
    date = mo_datestring_to_utc("2023-02-27T00:00:00+01:00")
    assert date is not None
    assert date.date() == datetime.date(2023, 2, 27)

    date = mo_datestring_to_utc("2023-02-27T00:00:00-03:00")
    assert date is not None
    assert date.date() == datetime.date(2023, 2, 27)

    date = mo_datestring_to_utc("2023-02-27T01:02:03-03:00")
    assert date is not None
    assert date == datetime.datetime(2023, 2, 27, 1, 2, 3)

    date = mo_datestring_to_utc(None)
    assert date is None


@pytest.mark.parametrize(
    "parts,dn",
    [
        (["CN=Nick", "", "DC=bar"], "CN=Nick,DC=bar"),
        (["CN=Nick", "OU=f", "DC=bar"], "CN=Nick,OU=f,DC=bar"),
        (["CN=Nick", "DC=bar"], "CN=Nick,DC=bar"),
        (["cn=Nick+uid=unique_id", "DC=bar"], "cn=Nick+uid=unique_id,DC=bar"),
        (["CN=van Dyck, Jeff", "DC=bar"], "CN=van Dyck\\, Jeff,DC=bar"),
        (["CN=van=Dyck=Jeff", "DC=bar"], "CN=van\\=Dyck\\=Jeff,DC=bar"),
        (
            ["", "CN=van=Dy+uid=ck, Jeff", "", "", "DC=bar", ""],
            "CN=van\\=Dy+uid=ck\\, Jeff,DC=bar",
        ),
    ],
)
def test_combine_dn_strings(parts: list[RDN], dn: DN) -> None:
    assert combine_dn_strings(parts) == dn


def test_remove_vowels() -> None:
    assert remove_vowels("food") == "fd"


def test_extract_ou_from_dn() -> None:
    assert extract_ou_from_dn("CN=Nick,OU=org,OU=main org,DC=f") == "OU=org,OU=main org"
    assert extract_ou_from_dn("CN=Nick,OU=org,DC=f") == "OU=org"
    assert extract_ou_from_dn("CN=Nick,DC=f") == ""

    with pytest.raises(LDAPInvalidDnError):
        extract_ou_from_dn("CN=Nick,OU=foo, DC=f")

    with pytest.raises(LDAPInvalidDnError):
        extract_ou_from_dn("")


@pytest.mark.parametrize(
    "mo_object,expected",
    [
        # When there are matching objects in MO, but the to-date is today, delete
        ({"validity": {"to": mo_today().isoformat()}}, True),
        # When there are matching objects in MO, but the to-date is tomorrow, do not delete
        (
            {"validity": {"to": (mo_today() + datetime.timedelta(days=1)).isoformat()}},
            False,
        ),
    ],
)
async def test_get_delete_flag(mo_object: dict[str, Any], expected: bool) -> None:
    # NOTE: This test fails close to midnight due to mo_datestring_to_utc being horrible
    # TODO: Fix mo_datestring_to_utc and the problems that lead to its creation
    flag = get_delete_flag(mo_object)
    assert flag is expected
