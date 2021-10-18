#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo._shared import OrgUnitHierarchy
from ramodels.mo._shared import OrgUnitLevel
from ramodels.mo._shared import OrgUnitType
from ramodels.mo._shared import ParentRef
from ramodels.mo._shared import Validity
from ramodels.mo.organisation_unit import OrganisationUnit
from tests.conftest import from_date_strat
from tests.conftest import not_from_regex
from tests.conftest import to_date_strat
from tests.conftest import unexpected_value_error
from tests.mo.details.test_association import association_strat
from tests.mo.details.test_engagement import engagement_assoc_strat
from tests.mo.details.test_engagement import engagement_strat
from tests.mo.details.test_manager import manager_strat

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def valid_details(draw):
    details_strat = (
        association_strat()
        | engagement_assoc_strat()
        | engagement_strat()
        | manager_strat()
    )
    return draw(details_strat)


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
        "uuid": st.uuids(),
        "user_key": st.text(),
        "name": st.text(),
        "org_unit_type_uuid": st.uuids(),
        "org_unit_level_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }
    optional = {
        "parent_uuid": st.none() | st.uuids(),
        "org_unit_hierarchy_uuid": st.none() | st.uuids(),
        "to_date": st.none() | to_date_strat(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestOrganisationUnit:
    @given(organisation_unit_strat())
    def test_init(self, model_dict):
        # Required
        assert OrganisationUnit(**model_dict)

    @given(organisation_unit_strat(), not_from_regex(r"^org_unit$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            OrganisationUnit(**model_dict)

    @given(organisation_unit_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert OrganisationUnit.from_simplified_fields(**simp_fields_dict)
