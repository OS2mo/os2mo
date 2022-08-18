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
from ramodels.mo.details.it_system import ITSystemRead


# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def read_strat(draw):
    required = {"name": st.text(), "user_key": st.text()}
    optional = {"type": st.just("itsystem"), "system_type": st.none() | st.text()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestITSystem:
    @given(read_strat())
    def test_read(self, model_dict):
        assert ITSystemRead(**model_dict)
