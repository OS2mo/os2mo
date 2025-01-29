# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError
from ramodels.mo._shared import KLEAspectRef
from ramodels.mo._shared import KLENumberRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import Validity
from ramodels.mo.details import KLEBase
from ramodels.mo.details import KLERead
from ramodels.mo.details import KLEWrite
from ramodels.mo.details.kle import KLE

from ramodels_tests.conftest import not_from_regex


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
        "kle_aspect_uuids": st.lists(st.uuids()),
        "org_unit_uuid": st.uuids(),
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "kle_number": st.builds(KLENumberRef),
        "kle_aspects": st.lists(st.builds(KLEAspectRef)),
    }
    optional = {
        "org_unit": st.none() | st.builds(OrgUnitRef),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def kle_strat(draw):
    required = {
        "kle_number": st.builds(KLENumberRef),
        "kle_aspect": st.lists(st.builds(KLEAspectRef)),
        "org_unit": st.builds(OrgUnitRef),
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("kle"),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestKLE:
    @given(kle_strat())
    def test_init(self, model_dict):
        assert KLE(**model_dict)

    @given(kle_strat(), not_from_regex(r"^kle"))
    def test_validators(self, model_dict, invalid_type):
        with pytest.raises(ValidationError, match="type may only be its default"):
            model_dict["type"] = invalid_type
            KLE(**model_dict)

    @given(base_strat())
    def test_base(self, model_dict):
        assert KLEBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert KLERead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict):
        assert KLEWrite(**model_dict)
