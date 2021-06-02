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

from .test__shared import valid_facet_attrs
from .test__shared import valid_facet_relations
from .test__shared import valid_facet_states
from ramodels.lora import Facet
from tests.conftest import from_date_strat
from tests.conftest import to_date_strat


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def facet_strat(draw):
    required = {
        "attributes": valid_facet_attrs(),
        "states": valid_facet_states(),
        "relations": valid_facet_relations(),
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def facet_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "user_key": st.text(),
        "organisation_uuid": st.uuids(),
    }
    optional = {"from_date": from_date_strat(), "to_date": to_date_strat()}

    # mypy has for some reason decided that required has an invalid type :(
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestFacet:
    @given(facet_strat())
    def test_init(self, model_dict):
        assert Facet(**model_dict)

    @given(facet_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Facet.from_simplified_fields(**simp_fields_dict)
