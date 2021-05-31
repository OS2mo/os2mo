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

from ramodels.mo.association import Association
from tests.conftest import unexpected_value_error
from tests.mo.test__shared import valid_assoc_type
from tests.mo.test__shared import valid_org_unit_ref
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_validity

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def association_strat(draw):
    required = {
        "org_unit": valid_org_unit_ref(),
        "person": valid_pers(),
        "association_type": valid_assoc_type(),
        "validity": valid_validity(),
    }
    optional = {"type": st.just("association")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def association_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "association_type_uuid": st.uuids(),
    }

    iso_dt = st.dates().map(lambda date: date.isoformat())
    optional = {"from_date": iso_dt, "to_date": iso_dt | st.none()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore

    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))

    return st_dict


class TestAssociation:
    @given(association_strat())
    def test_init(self, model_dict):
        assert Association(**model_dict)

    @given(association_strat(), st.text().filter(lambda s: s != "association"))
    def test_validators(self, model_dict, invalid_type):
        model_dict["type"] = invalid_type
        with unexpected_value_error():
            Association(**model_dict)

    @given(association_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Association.from_simplified_fields(**simp_fields_dict)
