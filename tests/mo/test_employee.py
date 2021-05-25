#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------
import re
from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from ramodels.mo.employee import Employee


# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def valid_cprs(draw):
    valid_date = draw(st.dates())
    valid_code = draw(st.from_regex(r"^\d{3}[1-9]$"))
    return valid_date.strftime("%d%m%y") + valid_code


class TestEmployee:
    invalid_cprs = st.text().filter(lambda s: re.match(r"^\d{9}[1-9]$", s) is None)

    @given(
        st.text().filter(lambda s: s != "employee"),
        st.text(),
        valid_cprs(),
        st.dates(),
    )
    def test_init(self, type, name, cpr_no, hy_date):
        # Required
        assert Employee(name=name)

        # Optional
        assert Employee(name=name, cpr_no=cpr_no, seniority=hy_date)

        # type value error
        with pytest.raises(ValidationError, match="unexpected value;"):
            Employee(type=type, name=name)

    @given(st.text(), invalid_cprs, st.dates())
    def test_validators(self, name, invalid_cpr, hy_date):
        with pytest.raises(ValidationError, match="string does not match regex"):
            Employee(name=name, cpr_no=invalid_cpr)

        empl = Employee(name=name, seniority=hy_date)
        assert isinstance(empl.seniority, datetime)
        assert empl.seniority.tzinfo
