#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime

import pytest
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from ramodels.mo._shared import AddressType
from ramodels.mo._shared import AssociationType
from ramodels.mo._shared import EngagementAssociationType
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import EngagementType
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import ManagerLevel
from ramodels.mo._shared import ManagerType
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import OrganisationRef
from ramodels.mo._shared import OrgUnitHierarchy
from ramodels.mo._shared import OrgUnitLevel
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import OrgUnitType
from ramodels.mo._shared import ParentRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import Responsibility
from ramodels.mo._shared import Validity
from ramodels.mo._shared import Visibility

# --------------------------------------------------------------------------------------
# MOBase
# --------------------------------------------------------------------------------------


class TestMOBase:
    def test_init(self):
        # MOBase cannot be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            MOBase()

    def test_fields(self):
        # Subclasses of MOBase should have a UUID field
        class MOSub(MOBase):
            pass

        assert MOSub.__fields__.get("uuid")


# --------------------------------------------------------------------------------------
# AddressType
# --------------------------------------------------------------------------------------


@st.composite
def address_type_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestAddressType:
    @given(address_type_strat())
    def test_init(self, model_dict):
        assert AddressType(**model_dict)


@st.composite
def valid_addr_type(draw):
    model_dict = draw(address_type_strat())
    return AddressType(**model_dict)


# --------------------------------------------------------------------------------------
# EngagementAssociationType
# --------------------------------------------------------------------------------------
@st.composite
def eng_assoc_type_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestEngagementAssociationType:
    @given(eng_assoc_type_strat())
    def test_init(self, model_dict):
        assert EngagementAssociationType(**model_dict)


@st.composite
def valid_eng_assoc_type(draw):
    model_dict = draw(eng_assoc_type_strat())
    return EngagementAssociationType(**model_dict)


# --------------------------------------------------------------------------------------
# EngagementRef
# --------------------------------------------------------------------------------------
@st.composite
def eng_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestEngagementRef:
    @given(eng_ref_strat())
    def test_init(self, model_dict):
        assert EngagementRef(**model_dict)


@st.composite
def valid_eng_ref(draw):
    model_dict = draw(eng_ref_strat())
    return EngagementRef(**model_dict)


# --------------------------------------------------------------------------------------
# EngagementType
# --------------------------------------------------------------------------------------


@st.composite
def eng_type_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestEngagementType:
    @given(eng_type_strat())
    def test_init(self, model_dict):
        assert EngagementType(**model_dict)


@st.composite
def valid_eng_type(draw):
    model_dict = draw(eng_type_strat())
    return EngagementType(**model_dict)


# --------------------------------------------------------------------------------------
# AssociationType
# --------------------------------------------------------------------------------------
@st.composite
def assoc_type_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestAssociationType:
    @given(assoc_type_strat())
    def test_init(self, model_dict):
        assert AssociationType(**model_dict)


@st.composite
def valid_assoc_type(draw):
    model_dict = draw(assoc_type_strat())
    return AssociationType(**model_dict)


# --------------------------------------------------------------------------------------
# JobFunction
# --------------------------------------------------------------------------------------
@st.composite
def job_function_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestJobFunction:
    @given(job_function_strat())
    def test_init(self, model_dict):
        assert JobFunction(**model_dict)


@st.composite
def valid_job_fun(draw):
    model_dict = draw(job_function_strat())
    return JobFunction(**model_dict)


# --------------------------------------------------------------------------------------
# ManagerLevel
# --------------------------------------------------------------------------------------
@st.composite
def manager_level_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestManagerLevel:
    @given(manager_level_strat())
    def test_init(self, model_dict):
        assert ManagerLevel(**model_dict)


@st.composite
def valid_man_level(draw):
    model_dict = draw(manager_level_strat())
    return ManagerLevel(**model_dict)


# --------------------------------------------------------------------------------------
# ManagerType
# --------------------------------------------------------------------------------------
@st.composite
def manager_type_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestManagerType:
    @given(manager_type_strat())
    def test_init(self, model_dict):
        assert ManagerType(**model_dict)


@st.composite
def valid_man_type(draw):
    model_dict = draw(manager_type_strat())
    return ManagerType(**model_dict)


# --------------------------------------------------------------------------------------
# OrganisationRef
# --------------------------------------------------------------------------------------
@st.composite
def org_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrganisationRef:
    @given(org_ref_strat())
    def test_init(self, model_dict):
        assert OrganisationRef(**model_dict)


@st.composite
def valid_org_ref(draw):
    model_dict = draw(org_ref_strat())
    return OrganisationRef(**model_dict)


# --------------------------------------------------------------------------------------
# OrgUnitHierarchy
# --------------------------------------------------------------------------------------
@st.composite
def org_unit_hierarchy_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrgUnitHierarchy:
    @given(org_unit_hierarchy_strat())
    def test_init(self, model_dict):
        assert OrgUnitHierarchy(**model_dict)


@st.composite
def valid_org_unit_hier(draw):
    model_dict = draw(org_unit_hierarchy_strat())
    return OrganisationRef(**model_dict)


# --------------------------------------------------------------------------------------
# OrgUnitLevel
# --------------------------------------------------------------------------------------
@st.composite
def org_unit_level_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrgUnitLevel:
    @given(org_unit_level_strat())
    def test_init(self, model_dict):
        assert OrgUnitLevel(**model_dict)


@st.composite
def valid_org_unit_level(draw):
    model_dict = draw(org_unit_level_strat())
    return OrgUnitLevel(**model_dict)


# --------------------------------------------------------------------------------------
# OrgUnitRef
# --------------------------------------------------------------------------------------
@st.composite
def org_unit_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrgUnitRef:
    @given(org_unit_ref_strat())
    def test_init(self, model_dict):
        assert OrgUnitRef(**model_dict)


@st.composite
def valid_org_unit_ref(draw):
    model_dict = draw(org_unit_ref_strat())
    return OrgUnitRef(**model_dict)


# --------------------------------------------------------------------------------------
# OrgUnitType
# --------------------------------------------------------------------------------------
@st.composite
def org_unit_type_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrgUnitType:
    @given(org_unit_type_strat())
    def test_init(self, model_dict):
        assert OrgUnitType(**model_dict)


@st.composite
def valid_org_unit_type(draw):
    model_dict = draw(org_unit_type_strat())
    return OrgUnitType(**model_dict)


# --------------------------------------------------------------------------------------
# ParentRef
# --------------------------------------------------------------------------------------
@st.composite
def parent_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestParentRef:
    @given(parent_ref_strat())
    def test_init(self, model_dict):
        assert ParentRef(**model_dict)


@st.composite
def valid_parent(draw):
    model_dict = draw(parent_ref_strat())
    return ParentRef(**model_dict)


# --------------------------------------------------------------------------------------
# PersonRef
# --------------------------------------------------------------------------------------
@st.composite
def person_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestPersonRef:
    @given(person_ref_strat())
    def test_init(self, model_dict):
        assert PersonRef(**model_dict)


@st.composite
def valid_pers(draw):
    model_dict = draw(person_ref_strat())
    return PersonRef(**model_dict)


# --------------------------------------------------------------------------------------
# Primary
# --------------------------------------------------------------------------------------
@st.composite
def primary_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestPrimary:
    @given(primary_strat())
    def test_init(self, model_dict):
        assert Primary(**model_dict)


@st.composite
def valid_primary(draw):
    model_dict = draw(primary_strat())
    return Primary(**model_dict)


# --------------------------------------------------------------------------------------
# Responsibility
# --------------------------------------------------------------------------------------
@st.composite
def responsibility_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestResponsibility:
    @given(responsibility_strat())
    def test_init(self, model_dict):
        assert Responsibility(**model_dict)


@st.composite
def valid_resp(draw):
    model_dict = draw(responsibility_strat())
    return Responsibility(**model_dict)


# --------------------------------------------------------------------------------------
# Validity
# --------------------------------------------------------------------------------------


@st.composite
def validity_strat(draw):
    required = dict()  # type: ignore
    optional = {"from_date": st.datetimes(), "to_date": st.datetimes() | st.none()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    # from_date must be less than or equal to to_date in all cases
    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(from_date <= to_date)
    if from_date is None and to_date:
        assume(to_date >= datetime(1930, 1, 1))
    return st_dict


class TestValidity:
    @given(validity_strat())
    def test_init(self, model_dict):
        assert Validity(**model_dict)

    @given(st.tuples(st.datetimes(), st.datetimes()), st.dates())
    def test_validators(self, dt_tup, from_date_no_tz):
        # tz unaware date becomes tz aware datetime
        validity = Validity(from_date=from_date_no_tz)
        assert isinstance(validity.from_date, datetime)
        assert validity.from_date.tzinfo

        # from_date > to_date should fail
        from_dt, to_dt = dt_tup
        assume(from_dt > to_dt)
        with pytest.raises(
            ValidationError, match="from_date must be less than or equal to to_date"
        ):
            Validity(from_date=from_dt, to_date=to_dt)


@st.composite
def valid_validity(draw):
    model_dict = draw(validity_strat())
    return Validity(**model_dict)


# --------------------------------------------------------------------------------------
# Visibility
# --------------------------------------------------------------------------------------
@st.composite
def visibility_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestVisibility:
    @given(visibility_strat())
    def test_init(self, model_dict):
        assert Visibility(**model_dict)


@st.composite
def valid_vis(draw):
    model_dict = draw(visibility_strat())
    return Visibility(**model_dict)
