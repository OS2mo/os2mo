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


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def facet_class_strat(draw):
    required = {"name": st.text(), "user_key": st.text(), "org_uuid": st.uuids()}
    optional = {"scope": st.text() | st.none()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestFacetClass:
    @given(facet_class_strat())
    def test_init(self, model_dict):
        assert FacetClass(**model_dict)
