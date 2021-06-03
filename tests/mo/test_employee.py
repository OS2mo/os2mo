#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------
from datetime import datetime

import pytest
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from ramodels.mo.employee import Employee
from tests.conftest import not_from_regex
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
        "cpr_no": st.none() | valid_cprs(),
        "seniority": st.none() | st.datetimes(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestEmployee:
    @given(employee_strat())
    @example({"name": "test", "cpr_no": "0101012101"})
    @example({"name": "test", "cpr_no": "0101014101"})
    @example({"name": "test", "cpr_no": "0101559101"})
    @example({"name": "test", "cpr_no": "0101016101"})
    @example({"name": "test", "cpr_no": "0101767101"})
    def test_init(self, model_dict):
        assert Employee(**model_dict)

    @given(employee_strat(), not_from_regex(r"^employee$"))
    def test_invalid_type(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Employee(**model_dict)

    @given(
        employee_strat(),
        not_from_regex(r"^\d{9}[1-9]$"),
        st.from_regex(r"^[3-9][2-9]\d{7}[1-9]$"),
    )
    def test_cpr_validation(self, model_dict, invalid_regex, invalid_date):
        with pytest.raises(ValidationError, match="string does not match regex"):
            model_dict["cpr_no"] = invalid_regex
            Employee(**model_dict)

        with pytest.raises(
            ValidationError, match=f"CPR number {invalid_date} is not valid"
        ):
            model_dict["cpr_no"] = invalid_date
            Employee(**model_dict)

    @given(employee_strat(), st.dates() | st.dates().map(lambda date: date.isoformat()))
    def test_validators(self, model_dict, sen_date):
        model_dict["seniority"] = sen_date
        empl = Employee(**model_dict)
        assert isinstance(empl.seniority, datetime)
        assert empl.seniority.tzinfo
