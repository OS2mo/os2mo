# -*- coding: utf-8 -*-
import datetime
import re
import time
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
import pytz  # type: ignore
from gql import gql
from graphql import print_ast
from ldap3.core.exceptions import LDAPInvalidDnError
from ramodels.mo.details.address import Address
from structlog.testing import capture_logs

from mo_ldap_import_export.exceptions import InvalidQuery
from mo_ldap_import_export.utils import add_filter_to_query
from mo_ldap_import_export.utils import combine_dn_strings
from mo_ldap_import_export.utils import countdown
from mo_ldap_import_export.utils import datetime_to_ldap_timestamp
from mo_ldap_import_export.utils import delete_keys_from_dict
from mo_ldap_import_export.utils import extract_ou_from_dn
from mo_ldap_import_export.utils import import_class
from mo_ldap_import_export.utils import listener
from mo_ldap_import_export.utils import mo_datestring_to_utc
from mo_ldap_import_export.utils import mo_object_is_valid
from mo_ldap_import_export.utils import remove_vowels


async def test_import_class():
    imported_class = import_class("ramodels.mo.employee.Employee")
    assert imported_class.__name__ == "Employee"


async def test_delete_keys_from_dict():
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


async def test_add_filter_to_query():

    query1 = gql(
        """
        query TestQuery {
          employees {
            uuid
          }
        }
        """
    )

    query2 = gql(
        """
        query TestQuery {
          employees (uuid:"uuid") {
            uuid
          }
        }
        """
    )

    # A query without filters cannot be modified
    with pytest.raises(InvalidQuery):
        modified_query = add_filter_to_query(query1, "to_date: null, from_date: null")

    modified_query = add_filter_to_query(query2, "to_date: null, from_date: null")
    modified_query_str = print_ast(modified_query)
    assert "from_date" in modified_query_str
    assert "to_date" in modified_query_str


async def test_mo_datestring_to_utc():

    date = mo_datestring_to_utc("2023-02-27T00:00:00+01:00")
    assert date.strftime("%Y-%m-%d") == "2023-02-27"

    date = mo_datestring_to_utc("2023-02-27T00:00:00-03:00")
    assert date.strftime("%Y-%m-%d") == "2023-02-27"

    date = mo_datestring_to_utc("2023-02-27T01:02:03-03:00")
    assert date.strftime("%Y-%m-%d %H:%M:%S") == "2023-02-27 01:02:03"

    date = mo_datestring_to_utc(None)
    assert date is None


async def test_mo_object_is_valid():

    mo_object = Address.from_simplified_fields("foo", uuid4(), "2021-01-01")
    assert mo_object_is_valid(mo_object) is True

    mo_object = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", to_date="2200-01-01"
    )
    assert mo_object_is_valid(mo_object) is True

    mo_object = Address.from_simplified_fields(
        "foo", uuid4(), "2021-01-01", to_date="2021-02-01"
    )
    assert mo_object_is_valid(mo_object) is False


async def test_datetime_to_ldap_timestamp():
    date = datetime.datetime(2021, 1, 1, 10, 45, 20)
    result = datetime_to_ldap_timestamp(date)
    assert result == "20210101104520.0-0000"

    date = datetime.datetime(2021, 1, 1, 10, 45, 20, 2000)
    result = datetime_to_ldap_timestamp(date)
    assert result == "20210101104520.2-0000"

    date = datetime.datetime(2021, 1, 1, 10, 45, 20, 2100)
    result = datetime_to_ldap_timestamp(date)
    assert result == "20210101104520.2-0000"

    date = datetime.datetime(2021, 1, 1, 10, 45, 20, 2100, pytz.timezone("Cuba"))
    result = datetime_to_ldap_timestamp(date)
    assert result == "20210101104520.2-0529"


async def test_listener():
    event_loop = MagicMock()
    sync_tool = MagicMock()
    user_context = {
        "event_loop": event_loop,
        "sync_tool": sync_tool,
    }

    context = {"user_context": user_context}

    event = {"attributes": {"distinguishedName": "CN=foo"}}
    with capture_logs() as cap_logs:
        listener(context, event)
        listener(context, {})

        messages = [w for w in cap_logs if w["log_level"] == "info"]
        assert re.match(
            "Registered change for LDAP object",
            str(messages[0]["event"]),
        )
        event_loop.create_task.assert_called()
        sync_tool.import_single_user.assert_called_with("CN=foo")

        assert re.match(
            "Got event without dn",
            str(messages[1]["event"]),
        )


async def test_countdown():
    t1 = time.time()
    await countdown(0.1, "foo")
    t2 = time.time()
    assert (t2 - t1) >= 0.1
    assert (t2 - t1) < 0.11

    t1 = time.time()
    t2 = time.time()
    assert (t2 - t1) < 0.1

    t1 = time.time()
    await countdown(0, "foo")
    t2 = time.time()
    assert (t2 - t1) < 0.1


def test_combine_dn_strings():
    assert combine_dn_strings(["CN=Nick", "", "DC=bar"]) == "CN=Nick,DC=bar"
    assert combine_dn_strings(["CN=Nick", "OU=f", "DC=bar"]) == "CN=Nick,OU=f,DC=bar"
    assert combine_dn_strings(["CN=Nick", "DC=bar"]) == "CN=Nick,DC=bar"


def test_remove_vowels():
    assert remove_vowels("food") == "fd"


def test_extract_ou_from_dn():
    assert extract_ou_from_dn("CN=Nick,OU=org,OU=main org,DC=f") == "OU=org,OU=main org"
    assert extract_ou_from_dn("CN=Nick,OU=org,DC=f") == "OU=org"
    assert extract_ou_from_dn("CN=Nick,DC=f") == ""

    with pytest.raises(LDAPInvalidDnError):
        extract_ou_from_dn("CN=Nick,OU=foo, DC=f")

    with pytest.raises(LDAPInvalidDnError):
        extract_ou_from_dn("")
