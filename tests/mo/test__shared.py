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
from tests.conftest import valid_dt_range

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


class TestAddressType:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert AddressType(uuid=hy_uuid)


@st.composite
def valid_addr_type(draw):
    uuid = draw(st.uuids())
    return AddressType(uuid=uuid)


# --------------------------------------------------------------------------------------
# EngagementAssociationType
# --------------------------------------------------------------------------------------


class TestEngagementAssociationType:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert EngagementAssociationType(uuid=hy_uuid)


@st.composite
def valid_eng_assoc_type(draw):
    uuid = draw(st.uuids())
    return EngagementAssociationType(uuid=uuid)


# --------------------------------------------------------------------------------------
# EngagementRef
# --------------------------------------------------------------------------------------


class TestEngagementRef:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert EngagementRef(uuid=hy_uuid)


@st.composite
def valid_eng(draw):
    uuid = draw(st.uuids())
    return EngagementRef(uuid=uuid)


# --------------------------------------------------------------------------------------
# EngagementType
# --------------------------------------------------------------------------------------


class TestEngagementType:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert EngagementType(uuid=hy_uuid)


@st.composite
def valid_eng_type(draw):
    uuid = draw(st.uuids())
    return EngagementType(uuid=uuid)


# --------------------------------------------------------------------------------------
# AssociationType
# --------------------------------------------------------------------------------------


class TestAssociationType:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert AssociationType(uuid=hy_uuid)


@st.composite
def valid_assoc_type(draw):
    uuid = draw(st.uuids())
    return AssociationType(uuid=uuid)


# --------------------------------------------------------------------------------------
# JobFunction
# --------------------------------------------------------------------------------------


class TestJobFunction:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert JobFunction(uuid=hy_uuid)


@st.composite
def valid_job_fun(draw):
    uuid = draw(st.uuids())
    return JobFunction(uuid=uuid)


# --------------------------------------------------------------------------------------
# ManagerLevel
# --------------------------------------------------------------------------------------


class TestManagerLevel:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert ManagerLevel(uuid=hy_uuid)


@st.composite
def valid_man_level(draw):
    uuid = draw(st.uuids())
    return ManagerLevel(uuid=uuid)


# --------------------------------------------------------------------------------------
# ManagerType
# --------------------------------------------------------------------------------------


class TestManagerType:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert ManagerType(uuid=hy_uuid)


@st.composite
def valid_man_type(draw):
    uuid = draw(st.uuids())
    return ManagerType(uuid=uuid)


# --------------------------------------------------------------------------------------
# OrganisationRef
# --------------------------------------------------------------------------------------


class TestOrganisationRef:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert OrganisationRef(uuid=hy_uuid)


@st.composite
def valid_org_ref(draw):
    uuid = draw(st.uuids())
    return OrganisationRef(uuid=uuid)


# --------------------------------------------------------------------------------------
# OrgUnitHierarchy
# --------------------------------------------------------------------------------------


class TestOrgUnitHierarchy:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert OrgUnitHierarchy(uuid=hy_uuid)


@st.composite
def valid_org_unit_hier(draw):
    uuid = draw(st.uuids())
    return OrganisationRef(uuid=uuid)


# --------------------------------------------------------------------------------------
# OrgUnitLevel
# --------------------------------------------------------------------------------------


class TestOrgUnitLevel:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert OrgUnitLevel(uuid=hy_uuid)


@st.composite
def valid_org_unit_level(draw):
    uuid = draw(st.uuids())
    return OrgUnitLevel(uuid=uuid)


# --------------------------------------------------------------------------------------
# OrgUnitRef
# --------------------------------------------------------------------------------------


class TestOrgUnitRef:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert OrgUnitRef(uuid=hy_uuid)


@st.composite
def valid_org_unit(draw):
    uuid = draw(st.uuids())
    return OrgUnitRef(uuid=uuid)


# --------------------------------------------------------------------------------------
# OrgUnitType
# --------------------------------------------------------------------------------------


class TestOrgUnitType:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert OrgUnitType(uuid=hy_uuid)


@st.composite
def valid_org_unit_type(draw):
    uuid = draw(st.uuids())
    return OrgUnitType(uuid=uuid)


# --------------------------------------------------------------------------------------
# ParentRef
# --------------------------------------------------------------------------------------


class TestParentRef:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert ParentRef(uuid=hy_uuid)


@st.composite
def valid_parent(draw):
    uuid = draw(st.uuids())
    return ParentRef(uuid=uuid)


# --------------------------------------------------------------------------------------
# PersonRef
# --------------------------------------------------------------------------------------


class TestPersonRef:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert PersonRef(uuid=hy_uuid)


@st.composite
def valid_pers(draw):
    uuid = draw(st.uuids())
    return PersonRef(uuid=uuid)


# --------------------------------------------------------------------------------------
# Primary
# --------------------------------------------------------------------------------------


class TestPrimary:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert Primary(uuid=hy_uuid)


@st.composite
def valid_primary(draw):
    uuid = draw(st.uuids())
    return Primary(uuid=uuid)


# --------------------------------------------------------------------------------------
# Responsibility
# --------------------------------------------------------------------------------------


class TestResponsibility:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert Responsibility(uuid=hy_uuid)


@st.composite
def valid_resp(draw):
    uuid = draw(st.uuids())
    return Responsibility(uuid=uuid)


# --------------------------------------------------------------------------------------
# Validity
# --------------------------------------------------------------------------------------


class TestValidity:
    @given(st.tuples(st.datetimes(), st.datetimes()))
    def test_init(self, dt_tup):
        from_dt, to_dt = dt_tup
        assume(from_dt <= to_dt)
        assert Validity(from_date=from_dt, to_date=to_dt)

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
    from_dt, to_dt = draw(valid_dt_range())
    return Validity(from_date=from_dt, to_date=to_dt)


# --------------------------------------------------------------------------------------
# Visibility
# --------------------------------------------------------------------------------------


class TestVisibility:
    @given(st.uuids())
    def test_init(self, hy_uuid):
        assert Visibility(uuid=hy_uuid)


@st.composite
def valid_vis(draw):
    uuid = draw(st.uuids())
    return Visibility(uuid=uuid)
