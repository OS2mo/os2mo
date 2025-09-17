# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import ITSystemRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo.details.it_system import ITUser
from ramodels.mo.details.it_system import ITUserBase
from ramodels.mo.details.it_system import ITUserRead
from ramodels.mo.details.it_system import ITUserWrite

from ramodels_tests.conftest import from_date_strat
from ramodels_tests.conftest import not_from_regex
from ramodels_tests.conftest import to_date_strat
from ramodels_tests.conftest import unexpected_value_error


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("it"),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "itsystem_uuid": st.uuids(),
    }
    optional = {
        "org_unit_uuid": st.none() | st.uuids(),
        "employee_uuid": st.none() | st.uuids(),
        "primary_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "itsystem": st.builds(ITSystemRef),
    }
    optional = {
        "org_unit": st.none() | st.builds(OrgUnitRef),
        "employee": st.none() | st.builds(EmployeeRef),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def it_user_strat(draw):
    required = {
        "user_key": st.text(),
        "itsystem": st.builds(ITSystemRef),
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("it"),
        "org_unit": st.none() | st.builds(OrgUnitRef),
        "person": st.none() | st.builds(PersonRef),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def it_user_fsf_strat(draw):
    required = {
        "user_key": st.text(),
        "itsystem_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }

    optional = {
        "uuid": st.none() | st.uuids(),
        "to_date": st.none() | to_date_strat(),
        "org_unit_uuid": st.none() | st.uuids(),
        "person_uuid": st.none() | st.uuids(),
        "engagement_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestITUser:
    @given(it_user_strat())
    def test_init(self, model_dict) -> None:
        assert ITUser(**model_dict)

    @given(it_user_strat(), not_from_regex(r"^it$"))
    def test_validators(self, model_dict, invalid_type) -> None:
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            ITUser(**model_dict)

    @given(it_user_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict) -> None:
        # Required
        assert ITUser.from_simplified_fields(**simp_fields_dict)

    @given(base_strat())
    def test_base(self, model_dict) -> None:
        assert ITUserBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict) -> None:
        assert ITUserRead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict) -> None:
        assert ITUserWrite(**model_dict)
