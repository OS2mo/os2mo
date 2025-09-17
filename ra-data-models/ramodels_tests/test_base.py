# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from dateutil.parser import isoparse
from dateutil.tz import tzoffset
from hypothesis import given
from hypothesis import strategies as st
from pydantic import Field
from pydantic import ValidationError
from ramodels.base import RABase
from ramodels.base import tz_isodate
from ramodels.exceptions import ISOParseError

from ramodels_tests.conftest import date_strat
from ramodels_tests.conftest import tz_dt_strat


class TestRABase:
    def test_init(self) -> None:
        # RABase should not be able to be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            RABase()


class TestConfig:
    class ConfigClass(RABase):
        test_field: str = Field(alias="Field alias")

    def test_frozen(self) -> None:
        config_class = self.ConfigClass(test_field="test")

        # config_class should be immutable
        with pytest.raises(TypeError, match="immutable"):
            config_class.test_field = "new test"  # type: ignore

        # and have a __hash__() method
        assert hasattr(config_class, "__hash__")

    def test_allow_population_by_field_name(self) -> None:
        # We should be able to populate using Field alias
        assert self.ConfigClass(**{"Field alias": "test"})

    def test_extra_forbid(self) -> None:
        # This is verboten
        with pytest.raises(ValidationError, match="extra fields not permitted"):
            self.ConfigClass(test_field="test", fail="oh no")  # type: ignore


def is_isodt_str(s: str) -> bool:
    try:
        datetime.fromisoformat(s)
    except Exception:
        try:
            isoparse(s)
        except Exception:
            return False
    return True


class TestTZISODate:
    @given(tz_dt_strat())
    def test_init(self, dt) -> None:
        iso_dt = tz_isodate(dt)
        assert iso_dt
        assert iso_dt.tzinfo

    @given(date_strat().map(lambda date: date.isoformat()))  # type: ignore
    def test_str_input(self, dt_str) -> None:
        iso_dt = tz_isodate(dt_str)
        assert iso_dt
        assert iso_dt.tzinfo

    @given(st.text().filter(lambda s: not is_isodt_str(s)))
    def test_fail_input(self, fail_str) -> None:
        with pytest.raises(ISOParseError):
            tz_isodate(fail_str)

    def test_pre_1894(self) -> None:
        assert tz_isodate("1885-05-01") == datetime(
            1885, 5, 1, 0, 0, tzinfo=ZoneInfo("Europe/Copenhagen")
        )
        assert tz_isodate("1885-05-01T00:00:00+00:50:20") == datetime(
            1885, 5, 1, 0, 0, tzinfo=tzoffset(None, 3600)
        )
