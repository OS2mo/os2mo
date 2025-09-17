# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo.organisation import OrganisationRead


@st.composite
def read_strat(draw):
    required = {
        "name": st.text(),
    }
    optional = {
        "type": st.just("organisation"),
        "user_key": st.none() | st.text(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestOrganisationUnit:
    @given(read_strat())
    def test_read(self, model_dict) -> None:
        assert OrganisationRead(**model_dict)
