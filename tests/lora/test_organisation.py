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

from .test__shared import valid_org_attrs
from .test__shared import valid_org_relations
from .test__shared import valid_org_states
from ramodels.lora import Organisation
from tests.conftest import from_date_strat
from tests.conftest import to_date_strat

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def organisation_strat(draw):
    required = {
        "attributes": valid_org_attrs(),
        "states": valid_org_states(),
    }
    optional = {"relations": st.none() | valid_org_relations()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def organisation_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "name": st.text(),
        "user_key": st.text(),
    }
    optional = {
        "municipality_code": st.none() | st.integers(),
        "from_date": from_date_strat(),
        "to_date": to_date_strat(),
    }

    # mypy has for some reason decided that required has an invalid type :(
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore

    return st_dict


class TestOrganisation:
    @given(organisation_strat())
    def test_init(self, model_dict):
        assert Organisation(**model_dict)

    @given(organisation_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Organisation.from_simplified_fields(**simp_fields_dict)
