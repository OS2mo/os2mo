# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# -*- coding: utf-8 -*-
import datetime
from unittest.mock import MagicMock

from mo_ldap_import_export.environments import construct_environment
from mo_ldap_import_export.environments import filter_mo_datestring
from mo_ldap_import_export.environments import filter_remove_curly_brackets
from mo_ldap_import_export.environments import filter_strip_non_digits


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


def test_bitwise_and():
    environment = construct_environment(MagicMock(), MagicMock())
    bitwise_template = environment.from_string("{{ input|int|bitwise_and(mask) }}")

    result = bitwise_template.render(input=0x01, mask=0x01)
    assert result == "1"

    result = bitwise_template.render(input=0x07, mask=0x03)
    assert result == "3"

    result = bitwise_template.render(input=0x08, mask=0x03)
    assert result == "0"
