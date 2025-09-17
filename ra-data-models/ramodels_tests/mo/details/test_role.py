# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import RoleType
from ramodels.mo._shared import Validity
from ramodels.mo.details import Role
from ramodels.mo.details import RoleBase
from ramodels.mo.details import RoleRead
from ramodels.mo.details import RoleWrite

from ramodels_tests.conftest import not_from_regex
from ramodels_tests.conftest import unexpected_value_error


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("role"),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit_uuid": st.uuids(),
        "employee_uuid": st.uuids(),
        "role_type_uuid": st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "employee": st.builds(EmployeeRef),
        "role_type": st.builds(RoleType),
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def role_strat(draw):
    required = {
        "user_key": st.text(),
        "role_type": st.builds(RoleType),
        "validity": st.builds(Validity),
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
    }
    optional = {
        "type": st.just("role"),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestRole:
    @given(base_strat())
    def test_base(self, model_dict) -> None:
        assert RoleBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict) -> None:
        assert RoleRead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict) -> None:
        assert RoleWrite(**model_dict)

    @given(role_strat())
    def test_init(self, model_dict) -> None:
        assert Role(**model_dict)

    @given(role_strat(), not_from_regex(r"^role$"))
    def test_validators(self, model_dict, invalid_type) -> None:
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Role(**model_dict)
