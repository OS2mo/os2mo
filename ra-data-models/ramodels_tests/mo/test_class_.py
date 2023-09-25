# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo import Validity
from ramodels.mo.class_ import ClassRead
from ramodels.mo.class_ import ClassWrite


OPTIONAL = {
    "published": st.none() | st.text(),
    "scope": st.none() | st.text(),
    "parent_uuid": st.none() | st.uuids(),
    "example": st.none() | st.text(),
    "owner": st.none() | st.uuids(),
}


@st.composite
def read_strat(draw):
    required = {
        "uuid": st.uuids(),
        "type": st.just("class"),
        "user_key": st.text(),
        "name": st.text(),
        "facet_uuid": st.uuids(),
        "org_uuid": st.uuids(),
        "validity": st.builds(Validity).filter(
            lambda validity: validity.from_date <= validity.to_date
            if validity.from_date and validity.to_date
            else True
        ),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=OPTIONAL))  # type: ignore
    return st_dict


@st.composite
def write_strat(draw):
    required = {
        "uuid": st.uuids(),
        "type": st.just("class"),
        "user_key": st.text(),
        "name": st.text(),
        "facet_uuid": st.uuids(),
        "org_uuid": st.uuids(),
        "validity": st.builds(Validity).filter(
            lambda validity: validity.from_date <= validity.to_date
            if validity.from_date and validity.to_date
            else True
        ),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=OPTIONAL))  # type: ignore
    return st_dict


class TestClass:
    @given(read_strat())
    def test_read(self, model_dict):
        assert ClassRead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict):
        assert ClassWrite(**model_dict)
