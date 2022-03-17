#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo.class_ import ClassRead

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def read_strat(draw):
    required = {
        "user_key": st.text(),
        "name": st.text(),
        "facet_uuid": st.uuids(),
        "org_uuid": st.uuids(),
    }
    optional = {
        "type": st.just("class"),
        "published": st.none() | st.text(),
        "scope": st.none() | st.text(),
        "parent_uuid": st.none() | st.uuids(),
        "example": st.none() | st.text(),
        "owner": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestClass:
    @given(read_strat())
    def test_read(self, model_dict):
        assert ClassRead(**model_dict)
