#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest
from dateutil.parser import isoparse as dt_isoparser
from hypothesis import given
from hypothesis import strategies as st
from pydantic import Field
from pydantic import ValidationError

from ramodels.base import RABase
from ramodels.base import tz_isodate
from ramodels.exceptions import ISOParseError

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestRABase:
    def test_init(self):
        # RABase should not be able to be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            RABase()


class TestConfig:
    class ConfigClass(RABase):
        test_field: str = Field(alias="Field alias")

    def test_frozen(self):
        config_class = self.ConfigClass(test_field="test")

        # config_class should be immutable
        with pytest.raises(TypeError, match="immutable"):
            config_class.test_field = "new test"  # type: ignore

        # and have a __hash__() method
        assert hasattr(config_class, "__hash__")

    def test_allow_population_by_field_name(self):
        # We should be able to populate using Field alias
        assert self.ConfigClass(**{"Field alias": "test"})

    def test_extra_forbid(self):
        # This is verboten
        with pytest.raises(ValidationError, match="extra fields not permitted"):
            self.ConfigClass(test_field="test", fail="oh no")  # type: ignore


def is_isodt_str(s):
    try:
        dt_isoparser(s)
    except Exception:
        return False
    return True


class TestTZISODate:
    @given(st.datetimes())
    def test_init(self, dt):
        iso_dt = tz_isodate(dt)
        assert iso_dt
        assert iso_dt.tzinfo

    @given(st.dates().map(lambda date: date.isoformat()))
    def test_str_input(self, dt_str):
        assert tz_isodate(dt_str)

    @given(st.text().filter(lambda s: not is_isodt_str(s)))
    def test_fail_input(self, fail_str):
        with pytest.raises(ISOParseError):
            tz_isodate(fail_str)
