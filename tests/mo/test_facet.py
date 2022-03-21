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

from ramodels.mo.facet import FacetClass
from ramodels.mo.facet import FacetRead


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def facet_class_strat(draw):
    required = {
        "facet_uuid": st.uuids(),
        "name": st.text(),
        "user_key": st.text(),
        "org_uuid": st.uuids(),
    }
    optional = {"scope": st.none() | st.text()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


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


class TestFacetClass:
    @given(facet_class_strat())
    def test_init(self, model_dict):
        assert FacetClass(**model_dict)


class TestFacetRead:
    @given(read_strat())
    def test_read(self, model_dict):
        assert FacetRead(**model_dict)
