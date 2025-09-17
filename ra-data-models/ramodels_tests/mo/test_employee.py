# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import OpenValidity
from ramodels.mo._shared import OrganisationRef
from ramodels.mo.details import AddressDetail
from ramodels.mo.details import AssociationDetail
from ramodels.mo.details import EngagementDetail
from ramodels.mo.details import ITUserDetail
from ramodels.mo.details import LeaveDetail
from ramodels.mo.details import ManagerDetail
from ramodels.mo.details import RoleDetail
from ramodels.mo.employee import Employee
from ramodels.mo.employee import EmployeeBase
from ramodels.mo.employee import EmployeeRead
from ramodels.mo.employee import EmployeeWrite


@st.composite
def valid_cprs(draw):
    valid_date = draw(st.dates())
    valid_code = draw(st.from_regex(r"^\d{3}[1-9]$"))
    return valid_date.strftime("%d%m%y") + valid_code


@st.composite
def valid_details(draw):
    details_strat = (
        st.builds(AddressDetail)
        | st.builds(AssociationDetail)
        | st.builds(EngagementDetail)
        | st.builds(ManagerDetail)
        | st.builds(ITUserDetail)
        | st.builds(RoleDetail)
        | st.builds(LeaveDetail)
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
def base_strat(draw):
    required = {"givenname": st.text(), "surname": st.text()}
    optional = {
        "type": st.just("employee"),
        "cpr_no": st.none() | valid_cprs(),
        "user_key": st.none() | st.text(),
        "seniority": st.none() | st.dates() | st.datetimes().map(str),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {"validity": st.builds(OpenValidity)}
    # To test that deprecated keys are removed properly
    # They can be anything
    optional = {"name": st.from_type(type), "nickname": st.from_type(type)}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    optional = {
        "details": st.none() | st.lists(valid_details()),
    }
    st_dict = draw(st.fixed_dictionaries({}, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


class TestEmployee:
    @given(employee_strat())
    def test_init(self, model_dict) -> None:
        assert Employee(**model_dict)

    @given(base_strat())
    def test_base(self, model_dict) -> None:
        assert EmployeeBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict) -> None:
        assert EmployeeRead(**model_dict)

    @given(write_strat(), st.text())
    def test_write(self, model_dict, name) -> None:
        assert EmployeeWrite(**model_dict)
        # We should be able to create a Write model
        # in the deprecated fashion.
        with pytest.deprecated_call():
            assert EmployeeWrite(name=name)
