# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import OrgUnitHierarchy
from ramodels.mo._shared import OrgUnitLevel
from ramodels.mo._shared import OrgUnitType
from ramodels.mo._shared import ParentRef
from ramodels.mo._shared import TimePlanning
from ramodels.mo._shared import Validity
from ramodels.mo.details import AssociationDetail
from ramodels.mo.details import EngagementDetail
from ramodels.mo.details import ITUserDetail
from ramodels.mo.details import ManagerDetail
from ramodels.mo.details import RoleDetail
from ramodels.mo.organisation_unit import OrganisationUnit
from ramodels.mo.organisation_unit import OrganisationUnitBase
from ramodels.mo.organisation_unit import OrganisationUnitRead
from ramodels.mo.organisation_unit import OrganisationUnitWrite

from ramodels_tests.conftest import from_date_strat
from ramodels_tests.conftest import to_date_strat


@st.composite
def valid_details(draw):
    details_strat = (
        st.builds(AssociationDetail)
        | st.builds(EngagementDetail)
        | st.builds(ManagerDetail)
        | st.builds(ITUserDetail)
        | st.builds(RoleDetail)
    )
    return draw(details_strat)


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
        "name": st.text(),
    }
    optional = {
        "type": st.just("org_unit"),
        "user_key": st.none() | st.text(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    optional = {
        "parent_uuid": st.uuids(),
        "org_unit_hierarchy": st.uuids(),
        "unit_type_uuid": st.uuids(),
        "org_unit_level_uuid": st.uuids(),
        "time_planning_uuid": st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries({}, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_start(draw):
    base_dict = draw(base_strat())
    optional = {
        "parent": st.builds(ParentRef),
        "org_unit_hierarchy": st.builds(OrgUnitHierarchy),
        "org_unit_type": st.builds(OrgUnitType),
        "org_unit_level": st.builds(OrgUnitLevel),
        "time_planning": st.builds(TimePlanning),
    }
    st_dict = draw(st.fixed_dictionaries({}, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def organisation_unit_strat(draw):
    required = {
        "user_key": st.text(),
        "validity": st.builds(Validity),
        "name": st.text(),
        "org_unit_type": st.builds(OrgUnitType),
        "org_unit_level": st.builds(OrgUnitLevel),
    }
    optional = {
        "type": st.just("org_unit"),
        "parent": st.none() | st.builds(ParentRef),
        "org_unit_hierarchy": st.none() | st.builds(OrgUnitHierarchy),
        "details": st.none() | st.lists(valid_details()),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def organisation_unit_fsf_strat(draw):
    required = {
        "user_key": st.text(),
        "name": st.text(),
        "org_unit_type_uuid": st.uuids(),
        "org_unit_level_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }
    optional = {
        "uuid": st.none() | st.uuids(),
        "parent_uuid": st.none() | st.uuids(),
        "org_unit_hierarchy_uuid": st.none() | st.uuids(),
        "to_date": st.none() | to_date_strat(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestOrganisationUnit:
    # backwards compatibility
    @given(organisation_unit_strat())
    def test_init(self, model_dict) -> None:
        assert OrganisationUnit(**model_dict)

    @given(organisation_unit_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict) -> None:
        assert OrganisationUnit.from_simplified_fields(**simp_fields_dict)

    # New tests
    @given(base_strat())
    def test_base(self, model_dict) -> None:
        assert OrganisationUnitBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict) -> None:
        assert OrganisationUnitRead(**model_dict)

    @given(write_start())
    def test_write(self, model_dict) -> None:
        assert OrganisationUnitWrite(**model_dict)
