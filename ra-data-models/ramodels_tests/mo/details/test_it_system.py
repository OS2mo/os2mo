# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import Validity
from ramodels.mo.details.it_system import ITSystemRead


@st.composite
def read_strat(draw):
    required = {
        "name": st.text(),
        "user_key": st.text(),
        "validity": st.builds(Validity),
    }
    optional = {"type": st.just("itsystem"), "system_type": st.none() | st.text()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestITSystem:
    @given(read_strat())
    def test_read(self, model_dict) -> None:
        assert ITSystemRead(**model_dict)
