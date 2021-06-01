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
from hypothesis import strategies as st

from .test__shared import valid_org_attrs
from .test__shared import valid_org_relations
from .test__shared import valid_org_states
from ramodels.lora import Organisation

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def organisation_strat(draw):
    required = {
        "attributes": valid_org_attrs(),
        "states": valid_org_states(),
    }
    optional = {"relations": valid_org_relations() | st.none()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def organisation_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "name": st.text(),
        "user_key": st.text(),
    }
    iso_dt = st.dates().map(lambda date: date.isoformat())
    optional = {
        "municipality_code": st.integers() | st.none(),
        "from_date": iso_dt,
        "to_date": iso_dt,
    }

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


class TestOrganisation:
    @given(organisation_strat())
    def test_init(self, model_dict):
        assert Organisation(**model_dict)

    @given(organisation_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Organisation.from_simplified_fields(**simp_fields_dict)
