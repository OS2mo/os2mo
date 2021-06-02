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

from .test__shared import valid_klasse_attrs
from .test__shared import valid_klasse_relations
from .test__shared import valid_klasse_states
from ramodels.lora import Klasse
from tests.conftest import from_date_strat
from tests.conftest import to_date_strat

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def klasse_strat(draw):
    required = {
        "attributes": valid_klasse_attrs(),
        "states": valid_klasse_states(),
        "relations": valid_klasse_relations(),
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def klasse_fsf_strat(draw):
    required = {
        "facet_uuid": st.uuids(),
        "uuid": st.uuids(),
        "user_key": st.text(),
        "organisation_uuid": st.uuids(),
        "title": st.text(),
    }
    optional = {
        "scope": st.text() | st.none(),
        "from_date": from_date_strat(),
        "to_date": to_date_strat(),
    }

    # mypy has for some reason decided that required has an invalid type :(
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore

    return st_dict


class TestKlasse:
    @given(klasse_strat())
    def test_init(self, model_dict):
        assert Klasse(**model_dict)

    @given(klasse_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Klasse.from_simplified_fields(**simp_fields_dict)
