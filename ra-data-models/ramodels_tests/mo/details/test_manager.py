# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import ManagerLevel
from ramodels.mo._shared import ManagerType
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Responsibility
from ramodels.mo._shared import Validity
from ramodels.mo.details import Manager
from ramodels.mo.details import ManagerBase
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import ManagerWrite

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
        "type": st.just("manager"),
        "user_key": st.none() | st.text(),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit_uuid": st.uuids(),
    }
    optional = {
        "employee_uuid": st.none() | st.uuids() | st.just(""),
        "manager_type_uuid": st.none() | st.uuids(),
        "manager_level_uuid": st.none() | st.uuids(),
        "responsibility_uuids": st.none() | st.lists(st.uuids()),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit": st.builds(OrgUnitRef),
    }
    optional = {
        "employee": st.none() | st.builds(EmployeeRef),
        "manager_level": st.none() | st.builds(ManagerLevel),
        "manager_type": st.none() | st.builds(ManagerType),
        "responsibility": st.none() | st.lists(st.builds(Responsibility)),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def manager_strat(draw):
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
        "responsibility": st.lists(st.builds(Responsibility)),
        "manager_level": st.builds(ManagerLevel),
        "manager_type": st.builds(ManagerType),
        "validity": st.builds(Validity),
    }
    optional = {"type": st.just("manager")}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def manager_fsf_strat(draw):
    required = {
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "responsibility_uuids": st.lists(st.uuids()),
        "manager_level_uuid": st.uuids(),
        "manager_type_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }

    optional = {
        "uuid": st.none() | st.uuids(),
        "to_date": st.none() | to_date_strat(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestManager:
    @given(base_strat())
    def test_base(self, model_dict):
        assert ManagerBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert ManagerRead(**model_dict)

    @given(read_strat())
    def test_read_empty_string_is_converted_to_none(self, model_dict):
        model_dict["employee_uuid"] = ""
        assert ManagerRead(**model_dict).employee_uuid is None

    @given(write_strat())
    def test_write(self, model_dict):
        assert ManagerWrite(**model_dict)

    @given(manager_strat())
    def test_init(self, model_dict):
        assert Manager(**model_dict)

    @given(manager_strat(), not_from_regex(r"^manager$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Manager(**model_dict)

    @given(manager_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        # Required
        assert Manager.from_simplified_fields(**simp_fields_dict)
