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
from tests.conftest import unexpected_value_error

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def valid_cprs(draw):
    valid_date = draw(st.dates())
    valid_code = draw(st.from_regex(r"^\d{3}[1-9]$"))
    return valid_date.strftime("%d%m%y") + valid_code


@st.composite
def employee_strat(draw):
    required = {"name": st.text()}
    optional = {
        "type": st.just("employee"),
        "cpr_no": valid_cprs() | st.none(),
        "seniority": st.datetimes() | st.none(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestEmployee:
    invalid_cprs = st.text().filter(lambda s: re.match(r"^\d{9}[1-9]$", s) is None)
    st.text().filter(lambda s: s != "employee")

    @given(employee_strat())
    def test_init(self, model_dict):
        assert Employee(**model_dict)

    @given(
        employee_strat(),
        st.text().filter(lambda s: s != "employee"),
        st.text().filter(lambda s: re.match(r"^\d{9}[1-9]$", s) is None),
        st.dates(),
    )
    def test_validators(self, model_dict, invalid_type, invalid_cpr, sen_date):
        with unexpected_value_error():
            _dict = model_dict.copy()
            _dict["type"] = invalid_type
            Employee(**_dict)
        with pytest.raises(ValidationError, match="string does not match regex"):
            _dict = model_dict.copy()
            _dict["cpr_no"] = invalid_cpr
            Employee(**_dict)

        model_dict["seniority"] = sen_date
        empl = Employee(**model_dict)
        assert isinstance(empl.seniority, datetime)
        assert empl.seniority.tzinfo
