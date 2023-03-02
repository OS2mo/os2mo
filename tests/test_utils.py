# -*- coding: utf-8 -*-
from uuid import uuid4

import pytest
from gql import gql
from graphql import print_ast
from ramodels.mo.details.address import Address

from mo_ldap_import_export.exceptions import InvalidQuery
from mo_ldap_import_export.utils import add_filter_to_query
from mo_ldap_import_export.utils import delete_keys_from_dict
from mo_ldap_import_export.utils import import_class
from mo_ldap_import_export.utils import mo_datestring_to_utc
from mo_ldap_import_export.utils import mo_object_is_valid


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
