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

from .test__shared import valid_fp
from .test__shared import valid_pub
from .test__shared import valid_resp
from ramodels.lora import Facet
from ramodels.lora._shared import FacetAttributes
from ramodels.lora._shared import FacetRelations
from ramodels.lora._shared import FacetStates


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def valid_fa(draw):
    fp_list = draw(st.lists(valid_fp(), min_size=1, max_size=1))
    return FacetAttributes(properties=fp_list)


@st.composite
def valid_fs(draw):
    pub_list = draw(st.lists(valid_pub(), min_size=1, max_size=1))
    return FacetStates(published_state=pub_list)


@st.composite
def valid_fr(draw):
    resp_list = draw(st.lists(valid_resp(), min_size=1, max_size=1))
    return FacetRelations(responsible=resp_list)


@st.composite
def valid_dt_range(draw):
    from_dt = draw(st.dates())
    to_dt = draw(st.dates())
    assume(from_dt < to_dt)
    return from_dt.isoformat(), to_dt.isoformat()


class TestFacet:
    @given(valid_fa(), valid_fs(), valid_fr())
    def test_init(self, valid_fa, valid_fs, valid_fr):
        assert Facet(attributes=valid_fa, states=valid_fs, relations=valid_fr)

    iso_dt = st.dates().map(lambda date: date.isoformat())

    @given(st.uuids(), st.text(), st.uuids(), valid_dt_range())
    def test_from_simplified_fields(self, uuid, user_key, org_uuid, dt_range):
        # This should be enough
        assert Facet.from_simplified_fields(uuid, user_key, org_uuid)

        # Optionals
        from_dt, to_dt = dt_range
        assert Facet.from_simplified_fields(uuid, user_key, org_uuid, from_dt, to_dt)
