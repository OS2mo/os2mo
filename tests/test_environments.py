# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
import datetime

import pandas as pd

from mo_ldap_import_export.environments import filter_mo_datestring
from mo_ldap_import_export.environments import filter_parse_datetime
from mo_ldap_import_export.environments import filter_remove_curly_brackets
from mo_ldap_import_export.environments import filter_splitfirst
from mo_ldap_import_export.environments import filter_splitlast
from mo_ldap_import_export.environments import filter_strip_non_digits


def test_splitfirst() -> None:
    assert filter_splitfirst("Test") == ["Test", ""]
    assert filter_splitfirst("Test Testersen") == [
        "Test",
        "Testersen",
    ]
    assert filter_splitfirst("Test Testersen med test") == [
        "Test",
        "Testersen med test",
    ]
    assert filter_splitfirst("") == ["", ""]
    assert filter_splitfirst("foo,bar,pub", separator=",") == [
        "foo",
        "bar,pub",
    ]


def test_splitlast() -> None:
    assert filter_splitlast("Test") == ["", "Test"]
    assert filter_splitlast("Test Testersen") == ["Test", "Testersen"]
    assert filter_splitlast("Test Testersen med test") == [
        "Test Testersen med",
        "test",
    ]
    assert filter_splitlast("") == ["", ""]
    assert filter_splitlast("foo,bar,pub", separator=",") == [
        "foo,bar",
        "pub",
    ]


def test_strip_non_digits() -> None:
    assert filter_strip_non_digits("01-01-01-1234") == "0101011234"
    assert filter_strip_non_digits("01/01/01-1234") == "0101011234"
    assert filter_strip_non_digits("010101-1234") == "0101011234"
    assert filter_strip_non_digits(101011234) is None


def test_filter_mo_datestring():
    output = filter_mo_datestring(datetime.datetime(2019, 4, 13, 20, 10, 10))
    # Note: Dates are always at midnight in MO
    assert output == "2019-04-13T00:00:00"
    assert filter_mo_datestring([]) is None
    assert filter_mo_datestring("") is None
    assert filter_mo_datestring(None) is None


def test_filter_remove_curly_brackets():
    assert filter_remove_curly_brackets("{foo}") == "foo"


def test_filter_parse_datetime():
    date = filter_parse_datetime("2021-01-01")
    assert date.strftime("%Y-%m-%d") == "2021-01-01"

    assert filter_parse_datetime("9999-12-31") == pd.Timestamp.max
    assert filter_parse_datetime("200-12-31") == pd.Timestamp.min
    assert filter_parse_datetime("") is None
    assert filter_parse_datetime("None") is None
    assert filter_parse_datetime("NONE") is None
    assert filter_parse_datetime([]) is None
    assert filter_parse_datetime(None) is None
