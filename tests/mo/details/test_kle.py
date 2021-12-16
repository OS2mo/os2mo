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

from ramodels.mo._shared import KLEAspectRef
from ramodels.mo._shared import KLENumberRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import Validity
from ramodels.mo.details import KLEBase
from ramodels.mo.details import KLERead
from ramodels.mo.details import KLEWrite

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("kle"),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "kle_number_uuid": st.uuids(),
        "kle_aspect_uuid": st.lists(st.uuids()),
    }
    optional = {
        "org_unit_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "kle_number": st.builds(KLENumberRef),
        "kle_aspect": st.lists(st.builds(KLEAspectRef)),
    }
    optional = {
        "org_unit": st.none() | st.builds(OrgUnitRef),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


class TestKLE:
    @given(base_strat())
    def test_base(self, model_dict):
        assert KLEBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert KLERead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict):
        assert KLEWrite(**model_dict)
