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

from .test__shared import valid_fref
from .test__shared import valid_klsprop
from .test__shared import valid_pub
from .test__shared import valid_resp
from ramodels.lora import Klasse
from ramodels.lora._shared import KlasseAttributes
from ramodels.lora._shared import KlasseRelations
from ramodels.lora._shared import KlasseStates

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def valid_ka(draw):
    kp_list = draw(st.lists(valid_klsprop(), min_size=1, max_size=1))
    return KlasseAttributes(properties=kp_list)


@st.composite
def valid_ks(draw):
    pub_list = draw(st.lists(valid_pub(), min_size=1, max_size=1))
    return KlasseStates(published_state=pub_list)


@st.composite
def valid_kr(draw):
    resp_list = draw(st.lists(valid_resp(), min_size=1, max_size=1))
    fref_list = draw(st.lists(valid_fref(), min_size=1, max_size=1))
    return KlasseRelations(responsible=resp_list, facet=fref_list)


@st.composite
def valid_dt_range(draw):
    from_dt = draw(st.dates())
    to_dt = draw(st.dates())
    assume(from_dt < to_dt)
    return from_dt.isoformat(), to_dt.isoformat()


class TestKlasse:
    @given(valid_ka(), valid_ks(), valid_kr())
    def test_init(self, valid_ka, valid_ks, valid_kr):
        assert Klasse(attributes=valid_ka, states=valid_ks, relations=valid_kr)

    @given(
        st.uuids(),
        st.uuids(),
        st.text(),
        st.text(),
        st.uuids(),
        st.text(),
        valid_dt_range(),
    )
    def test_from_simplified_fields(
        self, facet_uuid, uuid, user_key, scope, org_uuid, title, valid_dts
    ):
        # Required
        assert Klasse.from_simplified_fields(
            facet_uuid, uuid, user_key, org_uuid, title
        )

        # Optional
        from_dt, to_dt = valid_dts
        assert Klasse.from_simplified_fields(
            facet_uuid, uuid, user_key, org_uuid, title, scope, from_dt, to_dt
        )
