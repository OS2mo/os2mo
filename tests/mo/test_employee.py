#!/usr/bin/env python3
# ---------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------
import pytest
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from ramodels.mo._shared import OrganisationRef
from ramodels.mo.employee import Employee
from tests.conftest import not_from_regex
from tests.conftest import unexpected_value_error
from tests.mo.details.test_address import address_strat
from tests.mo.details.test_association import association_strat
from tests.mo.details.test_engagement import engagement_assoc_strat
from tests.mo.details.test_engagement import engagement_strat
from tests.mo.details.test_it_system import it_system_strat
from tests.mo.details.test_manager import manager_strat
from tests.mo.details.test_role import role_strat

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def valid_cprs(draw):
    valid_date = draw(st.dates())
    valid_code = draw(st.from_regex(r"^\d{3}[1-9]$"))
    return valid_date.strftime("%d%m%y") + valid_code


@st.composite
def valid_details(draw):
    details_strat = (
        address_strat()
        | association_strat()
        | engagement_assoc_strat()
        | engagement_strat()
        | manager_strat()
        | it_system_strat()
        | role_strat()
    )
    return draw(details_strat)


@st.composite
def employee_strat(draw):
    required = {"givenname": st.text(), "surname": st.text()}
    optional = {
        "type": st.just("employee"),
        "cpr_no": st.none() | valid_cprs(),
        "user_key": st.none() | st.text(),
        "org": st.none() | st.builds(OrganisationRef),
        "details": st.none() | st.lists(valid_details()),
        "seniority": st.none() | st.datetimes(),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def invalid_name_combo(draw):
    name_strats = st.just("givenname"), st.just("surname")
    name_dict = draw(
        st.dictionaries(keys=st.one_of(*name_strats), values=st.text(), min_size=1)
    )
    name_dict["name"] = draw(st.text())
    return name_dict


class TestEmployee:
    @given(employee_strat())
    @example({"givenname": "test", "surname": "testesen", "cpr_no": "0101012101"})
    @example({"givenname": "test", "surname": "testesen", "cpr_no": "0101014101"})
    @example({"givenname": "test", "surname": "testesen", "cpr_no": "0101559101"})
    @example({"givenname": "test", "surname": "testesen", "cpr_no": "0101016101"})
    @example({"givenname": "test", "surname": "testesen", "cpr_no": "0101767101"})
    def test_init(self, model_dict):
        assert Employee(**model_dict)

    @given(st.text(), employee_strat())
    def test_deprecation_warning(self, name, model_dict):
        # It should be possible to initialise an Employee with just a name
        # but we should get a deprecation warning
        with pytest.deprecated_call():
            assert Employee(name=name)
        # Similarly, we should be able to declare a nickname, but get a
        # deprecation warning when we do so
        model_dict["nickname"] = name
        with pytest.deprecated_call():
            assert Employee(**model_dict)

    @given(invalid_name_combo())
    def test_name_validations(self, invalid_dict):
        with pytest.raises(ValidationError, match="mutually exclusive"):
            Employee(**invalid_dict)
        invalid_dict["name"] = None
        assert Employee(**invalid_dict)

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

        with pytest.raises(ValidationError, match="CPR number is invalid"):
            model_dict["cpr_no"] = invalid_date
            Employee(**model_dict)
