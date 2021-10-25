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

from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import LeaveType
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo.details import Leave
from tests.conftest import not_from_regex
from tests.conftest import unexpected_value_error

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


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
    @given(leave_strat())
    def test_init(self, model_dict):
        assert Leave(**model_dict)

    @given(leave_strat(), not_from_regex(r"^leave$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Leave(**model_dict)
