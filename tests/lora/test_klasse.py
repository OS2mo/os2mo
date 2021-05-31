#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date

from hypothesis import assume
from hypothesis import given
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis import strategies as st

from .test__shared import valid_klasse_attrs
from .test__shared import valid_klasse_relations
from .test__shared import valid_klasse_states
from ramodels.lora import Klasse

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
    iso_dt = st.dates().map(lambda date: date.isoformat())
    optional = {"scope": st.text() | st.none(), "from_date": iso_dt, "to_date": iso_dt}

    # mypy has for some reason decided that required has an invalid type :(
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore

    # from_date must be strictly less than to_date in all cases
    if st_dict.get("to_date") and st_dict.get("from_date") is None:
        assume(date.fromisoformat(st_dict["to_date"]) > date(1930, 1, 1))
    if all([st_dict.get("from_date"), st_dict.get("to_date")]):
        assume(
            date.fromisoformat(st_dict["from_date"])
            < date.fromisoformat(st_dict["to_date"])
        )
    return st_dict


class TestKlasse:
    # Data generation will be slow due to the nested nature of LoRa models
    @settings(suppress_health_check=[HealthCheck.too_slow])
    @given(klasse_strat())
    def test_init(self, model_dict):
        assert Klasse(**model_dict)

    @given(klasse_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Klasse.from_simplified_fields(**simp_fields_dict)
