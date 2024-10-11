# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-

import pytest
from ldap3.core.exceptions import LDAPInvalidDnError

from mo_ldap_import_export.utils import combine_dn_strings
from mo_ldap_import_export.utils import delete_keys_from_dict
from mo_ldap_import_export.utils import exchange_ou_in_dn
from mo_ldap_import_export.utils import extract_ou_from_dn
from mo_ldap_import_export.utils import import_class
from mo_ldap_import_export.utils import mo_datestring_to_utc
from mo_ldap_import_export.utils import remove_vowels


async def test_import_class() -> None:
    imported_class = import_class("ramodels.mo.employee.Employee")
    assert imported_class.__name__ == "Employee"

    imported_class = import_class("Custom.JobTitleFromADToMO")
    assert imported_class.__name__ == "JobTitleFromADToMO"

    with pytest.raises(NotImplementedError) as exc_info:
        import_class("Ashbringer")
    assert "Unknown argument to import_class" in str(exc_info.value)


async def test_delete_keys_from_dict() -> None:
    dict_to_delete_from = {
        "foo": 1,
        "bar": 2,
        "nest": {"foo": 1, "bar": 2},
    }

    modified_dict = delete_keys_from_dict(dict_to_delete_from, ["foo"])

    assert "foo" in dict_to_delete_from
    assert "foo" in dict_to_delete_from["nest"]  # type:ignore
    assert "foo" not in modified_dict
    assert "foo" not in modified_dict["nest"]


async def test_mo_datestring_to_utc() -> None:
    date = mo_datestring_to_utc("2023-02-27T00:00:00+01:00")
    assert date is not None
    assert date.strftime("%Y-%m-%d") == "2023-02-27"

    date = mo_datestring_to_utc("2023-02-27T00:00:00-03:00")
    assert date is not None
    assert date.strftime("%Y-%m-%d") == "2023-02-27"

    date = mo_datestring_to_utc("2023-02-27T01:02:03-03:00")
    assert date is not None
    assert date.strftime("%Y-%m-%d %H:%M:%S") == "2023-02-27 01:02:03"

    date = mo_datestring_to_utc(None)
    assert date is None


def test_combine_dn_strings() -> None:
    assert combine_dn_strings(["CN=Nick", "", "DC=bar"]) == "CN=Nick,DC=bar"
    assert combine_dn_strings(["CN=Nick", "OU=f", "DC=bar"]) == "CN=Nick,OU=f,DC=bar"
    assert combine_dn_strings(["CN=Nick", "DC=bar"]) == "CN=Nick,DC=bar"


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


def test_exchange_ou_in_dn() -> None:
    assert (
        exchange_ou_in_dn("CN=Tobias,OU=foo,DC=Q", "OU=bar") == "CN=Tobias,OU=bar,DC=Q"
    )
    assert (
        exchange_ou_in_dn("CN=Tobias,OU=foo,DC=Q", "OU=mucki,OU=bar")
        == "CN=Tobias,OU=mucki,OU=bar,DC=Q"
    )
    assert (
        exchange_ou_in_dn("CN=Tobias,OU=foo,OU=oof,DC=Q", "OU=mucki")
        == "CN=Tobias,OU=mucki,DC=Q"
    )
    assert (
        exchange_ou_in_dn("CN=Tobias,OU=foo,OU=oof", "OU=mucki,OU=bar")
        == "CN=Tobias,OU=mucki,OU=bar"
    )
    assert (
        exchange_ou_in_dn("CN=Tobias,OU=bar,DC=Q", "OU=bar") == "CN=Tobias,OU=bar,DC=Q"
    )
