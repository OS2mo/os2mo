#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import LeaveType
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo.details import Leave
from ramodels.mo.details import LeaveBase
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import LeaveWrite
from tests.conftest import not_from_regex
from tests.conftest import unexpected_value_error

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("leave"),
        "user_key": st.none() | st.text(),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "employee_uuid": st.uuids(),
        "leave_type_uuid": st.uuids(),
    }
    optional = {
        "engagement_uuid": st.none() | st.uuids(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "employee": st.builds(EmployeeRef),
        "leave_type": st.builds(LeaveType),
    }
    optional = {
        "engagement": st.none() | st.builds(EngagementRef),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def leave_strat(draw):
    required = {
        "user_key": st.text(),
        "leave_type": st.builds(LeaveType),
        "validity": st.builds(Validity),
        "person": st.builds(PersonRef),
    }
    optional = {"type": st.just("leave"), "engagement": st.builds(EngagementRef)}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestLeave:
    @given(base_strat())
    def test_base(self, model_dict):
        assert LeaveBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert LeaveRead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict):
        assert LeaveWrite(**model_dict)

    @given(leave_strat())
    def test_init(self, model_dict):
        assert Leave(**model_dict)

    @given(leave_strat(), not_from_regex(r"^leave$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Leave(**model_dict)
