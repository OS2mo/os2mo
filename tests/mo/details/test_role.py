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

from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import RoleType
from ramodels.mo._shared import Validity
from ramodels.mo.details import Role
from tests.conftest import not_from_regex
from tests.conftest import unexpected_value_error

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def role_strat(draw):
    required = {
        "user_key": st.text(),
        "role_type": st.builds(RoleType),
        "validity": st.builds(Validity),
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
    }
    optional = {
        "type": st.just("role"),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestRole:
    @given(role_strat())
    def test_init(self, model_dict):
        assert Role(**model_dict)

    @given(role_strat(), not_from_regex(r"^role$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Role(**model_dict)
