#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo.address import Address
from tests.conftest import unexpected_value_error
from tests.mo.test__shared import valid_addr_type
from tests.mo.test__shared import valid_eng_ref
from tests.mo.test__shared import valid_org_ref
from tests.mo.test__shared import valid_org_unit_ref
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_validity
from tests.mo.test__shared import valid_vis

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def address_strat(draw):
    required = {
        "value": st.text(),
        "address_type": valid_addr_type(),
        "org": valid_org_ref(),
        "validity": valid_validity(),
    }

    optional = {
        "type": st.just("address"),
        "value2": st.text() | st.none(),
        "person": valid_pers() | st.none(),
        "org_unit": valid_org_unit_ref() | st.none(),
        "engagement": valid_eng_ref() | st.none(),
        "visibility": valid_vis() | st.none(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def address_fsf_strat(draw):
    iso_dt = st.dates().map(lambda date: date.isoformat())
    required = {
        "uuid": st.uuids(),
        "value": st.text(),
        "address_type_uuid": st.uuids(),
        "org_uuid": st.uuids(),
        "from_date": iso_dt,
    }
    optional = {
        "to_date": iso_dt | st.none(),
        "value2": st.text() | st.none(),
        "person_uuid": st.uuids() | st.none(),
        "org_unit_uuid": st.uuids() | st.none(),
        "engagement_uuid": st.uuids() | st.none(),
        "visibility_uuid": st.uuids() | st.none(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(from_date <= to_date)
    return st_dict


class TestAddress:
    @given(address_strat())
    def test_init(self, model_dict):
        assert Address(**model_dict)

    @given(address_strat(), st.text().filter(lambda s: s != "address"))
    def test_validators(self, model_dict, invalid_type):
        model_dict["type"] = invalid_type
        with unexpected_value_error():
            Address(**model_dict)

    @given(address_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Address.from_simplified_fields(**simp_fields_dict)
