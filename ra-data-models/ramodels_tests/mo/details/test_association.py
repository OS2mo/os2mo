# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

import pytest
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import AssociationType
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import ITUserRef
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import Validity
from ramodels.mo.details import Association
from ramodels.mo.details import AssociationBase
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import AssociationWrite

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
        "type": st.just("association"),
        "user_key": st.none() | st.text(),
        "dynamic_class_uuid": st.none() | st.uuids(),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit_uuid": st.uuids(),
        "employee_uuid": st.uuids() | st.just(""),
    }
    optional = {
        "association_type_uuid": st.none() | st.uuids(),
        "primary_uuid": st.none() | st.uuids(),
        "substitute_uuid": st.none() | st.uuids(),
        "job_function_uuid": st.none() | st.uuids(),
        "it_user_uuid": st.none() | st.uuids(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def _base_write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "employee": st.builds(EmployeeRef),
        "association_type": st.builds(AssociationType),
    }
    optional = {
        "primary": st.none() | st.builds(Primary),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    normal_assoc_fields = {
        "substitute": st.none() | st.builds(EmployeeRef),
    }
    it_assoc_fields = {
        "job_function": st.none() | st.builds(JobFunction),
        "it_user": st.none() | st.builds(ITUserRef),
    }
    optional = st.one_of(  # type: ignore
        st.fixed_dictionaries(normal_assoc_fields),  # type: ignore
        st.fixed_dictionaries(it_assoc_fields),  # type: ignore
    )
    base_dict = draw(_base_write_strat())
    optional_dict = draw(optional)
    return {**base_dict, **optional_dict}


@st.composite
def write_strat_invalid(draw):
    normal_assoc_fields = {"substitute": st.builds(EmployeeRef)}
    it_assoc_fields = {
        "job_function": st.builds(JobFunction),
        "it_user": st.builds(ITUserRef),
    }
    normal_assoc = draw(st.fixed_dictionaries(normal_assoc_fields))  # type: ignore
    it_assoc = draw(st.fixed_dictionaries(it_assoc_fields))  # type: ignore
    base_dict = draw(_base_write_strat())
    return {**base_dict, **normal_assoc, **it_assoc}


@st.composite
def association_strat(draw):
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
        "association_type": st.builds(AssociationType),
        "validity": st.builds(Validity),
    }
    optional = {"type": st.just("association")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def association_fsf_strat(draw):
    required = {
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "association_type_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }

    optional = {
        "uuid": st.none() | st.uuids(),
        "to_date": st.none() | to_date_strat(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore

    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))

    return st_dict


class TestAssociation:
    @given(association_strat())
    def test_init(self, model_dict):
        assert Association(**model_dict)

    @given(association_strat(), not_from_regex(r"^association$"))
    def test_invalid_type(self, model_dict, invalid_type):
        model_dict["type"] = invalid_type
        with unexpected_value_error():
            Association(**model_dict)

    @given(association_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Association.from_simplified_fields(**simp_fields_dict)

    @given(base_strat())
    def test_base(self, model_dict):
        assert AssociationBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert AssociationRead(**model_dict)

    @given(read_strat())
    def test_read_empty_string_is_converted_to_none(self, model_dict):
        model_dict["employee_uuid"] = ""
        assert AssociationRead(**model_dict).employee_uuid is None

    @given(write_strat())
    def test_write(self, model_dict):
        assert AssociationWrite(**model_dict)

    @given(write_strat_invalid())
    def test_write_validates_mutually_exclusive_fields(self, model_dict):
        with pytest.raises(ValueError):
            AssociationWrite(**model_dict)
