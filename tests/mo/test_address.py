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

from ramodels.mo._shared import AddressType
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import OrganisationRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo._shared import Visibility
from ramodels.mo.address import Address
from tests.conftest import from_date_strat
from tests.conftest import to_date_strat
from tests.conftest import unexpected_value_error

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def address_strat(draw):
    required = {
        "value": st.text(),
        "address_type": st.builds(AddressType),
        "org": st.builds(OrganisationRef),
        "validity": st.builds(Validity),
    }

    optional = {
        "type": st.just("address"),
        "value2": st.none() | st.text(),
        "person": st.none() | st.builds(PersonRef),
        "org_unit": st.none() | st.builds(OrgUnitRef),
        "engagement": st.none() | st.builds(EngagementRef),
        "visibility": st.none() | st.builds(Visibility),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def address_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "value": st.text(),
        "address_type_uuid": st.uuids(),
        "org_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }
    optional = {
        "to_date": st.none() | to_date_strat(),
        "value2": st.none() | st.text(),
        "person_uuid": st.none() | st.uuids(),
        "org_unit_uuid": st.none() | st.uuids(),
        "engagement_uuid": st.none() | st.uuids(),
        "visibility_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestAddress:
    @given(address_strat())
    def test_init(self, model_dict):
        assert Address(**model_dict)

    @given(address_strat(), st.text().filter(lambda s: s != "address"))
    def test_invalid_type(self, model_dict, invalid_type):
        model_dict["type"] = invalid_type
        with unexpected_value_error():
            Address(**model_dict)

    @given(address_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Address.from_simplified_fields(**simp_fields_dict)
