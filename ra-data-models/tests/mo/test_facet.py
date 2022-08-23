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
from ramodels.mo._shared import AlphaStr
from ramodels.mo.facet import FacetRead
from ramodels.mo.facet import FacetWrite


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def read_strat(draw):
    required = {
        "user_key": st.text(),
        "org_uuid": st.uuids(),
        "description": st.text(),
    }
    optional = {
        "type": st.just("facet"),
        "published": st.none() | st.text(),
        "parent_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def facet_write_strat(draw):
    required = {
        "uuid": st.uuids(),
        "type_": st.just("facet"),
        "description": st.from_regex(AlphaStr.regex),
        "user_key": st.text(),
        "org_uuid": st.uuids(),
    }
    optional = {
        "published": st.none() | st.text(),
        "parent_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestFacetRead:
    @given(read_strat())
    def test_read(self, model_dict):
        assert FacetRead(**model_dict)


class TestFacetWrite:
    @given(facet_write_strat())
    def test_write(self, model_dict):
        assert FacetWrite(**model_dict)
