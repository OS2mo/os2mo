# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import Validity
from ramodels.mo.details.related_unit import RelatedUnitBase
from ramodels.mo.details.related_unit import RelatedUnitRead
from ramodels.mo.details.related_unit import RelatedUnitWrite


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("related_unit"),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit_uuids": st.lists(st.uuids()),
    }

    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_units": st.lists(st.builds(OrgUnitRef)),
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return {**base_dict, **st_dict}


class TestRELATED_UNIT:
    @given(base_strat())
    def test_base(self, model_dict):
        assert RelatedUnitBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert RelatedUnitRead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict):
        assert RelatedUnitWrite(**model_dict)
