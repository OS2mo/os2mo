# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError
from ramodels.mo._shared import AddressType
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import OrganisationRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo._shared import Visibility
from ramodels.mo.details.address import Address
from ramodels.mo.details.address import AddressBase
from ramodels.mo.details.address import AddressRead
from ramodels.mo.details.address import AddressWrite

from ramodels_tests.conftest import from_date_strat
from ramodels_tests.conftest import not_from_regex
from ramodels_tests.conftest import to_date_strat
from ramodels_tests.conftest import unexpected_value_error


@st.composite
def base_strat(draw):
    required = {"value": st.text(), "validity": st.builds(Validity)}
    optional = {"type": st.just("address"), "value2": st.none() | st.text()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {"address_type_uuid": st.uuids()}
    optional = {
        "employee_uuid": st.none() | st.uuids(),
        "org_unit_uuid": st.none() | st.uuids(),
        "engagement_uuid": st.none() | st.uuids(),
        "visibility_uuid": st.none() | st.uuids(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {"address_type": st.builds(AddressType)}
    employee = st.fixed_dictionaries({"employee": st.builds(EmployeeRef)})
    org_unit = st.fixed_dictionaries({"org_unit": st.builds(OrgUnitRef)})
    optional = {
        "visibility": st.none() | st.builds(Visibility),
        "engagement": st.none() | st.builds(EngagementRef),
    }
    ref_dict = draw(st.one_of(employee, org_unit))
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict, **ref_dict}


def ref_check_strat():
    required = {
        "employee": st.builds(EmployeeRef),
        "org_unit": st.builds(OrgUnitRef),
    }
    return st.fixed_dictionaries(required)  # type: ignore


@st.composite
def address_strat(draw):
    required = {
        "value": st.text(),
        "address_type": st.builds(AddressType),
        "validity": st.builds(Validity),
    }

    optional = {
        "type": st.just("address"),
        "value2": st.none() | st.text(),
        "person": st.none() | st.builds(PersonRef),
        "org_unit": st.none() | st.builds(OrgUnitRef),
        "engagement": st.none() | st.builds(EngagementRef),
        "visibility": st.none() | st.builds(Visibility),
        "org": st.none() | st.builds(OrganisationRef),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def address_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "value": st.text(),
        "address_type_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }
    optional = {
        "to_date": st.none() | to_date_strat(),
        "value2": st.none() | st.text(),
        "person_uuid": st.none() | st.uuids(),
        "org_unit_uuid": st.none() | st.uuids(),
        "engagement_uuid": st.none() | st.uuids(),
        "visibility_uuid": st.none() | st.uuids(),
        "org_uuid": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestAddress:
    @given(address_strat())
    def test_init(self, model_dict):
        assert Address(**model_dict)

    @given(address_strat(), not_from_regex(r"^address$"))
    def test_invalid_type(self, model_dict, invalid_type):
        model_dict["type"] = invalid_type
        with unexpected_value_error():
            Address(**model_dict)

    @given(address_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Address.from_simplified_fields(**simp_fields_dict)

    @given(base_strat())
    def test_base(self, model_dict):
        assert AddressBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert AddressRead(**model_dict)

    @given(write_strat(), ref_check_strat())
    def test_write(self, model_dict, refs_dict):
        assert AddressWrite(**model_dict)
        # Too many references given.
        too_many_refs = {**model_dict, **refs_dict}
        with pytest.raises(ValidationError, match="Too many references"):
            AddressWrite(**too_many_refs)
        # Not enough references given.
        too_few_refs = model_dict
        for k in refs_dict:
            too_few_refs.pop(k, None)
        with pytest.raises(ValidationError, match="A reference must"):
            AddressWrite(**too_few_refs)
