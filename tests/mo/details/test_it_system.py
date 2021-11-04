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

from ramodels.mo._shared import ITSystemRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo.details import ITSystemBinding
from tests.conftest import from_date_strat
from tests.conftest import not_from_regex
from tests.conftest import to_date_strat
from tests.conftest import unexpected_value_error


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def it_system_strat(draw):
    required = {
        "user_key": st.text(),
        "itsystem": st.builds(ITSystemRef),
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("it"),
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def it_system_fsf_strat(draw):
    required = {
        "user_key": st.text(),
        "itsystem_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }

    optional = {
        "uuid": st.uuids(),
        "to_date": st.none() | to_date_strat(),
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestITSystemBinding:
    @given(it_system_strat())
    def test_init(self, model_dict):
        assert ITSystemBinding(**model_dict)

    @given(it_system_strat(), not_from_regex(r"^it$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            ITSystemBinding(**model_dict)

    @given(it_system_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        # Required
        assert ITSystemBinding.from_simplified_fields(**simp_fields_dict)
