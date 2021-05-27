#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from ramodels.mo.organisation_unit import OrganisationUnit
from tests.conftest import valid_dt_range
from tests.mo.test__shared import valid_org_unit_hier
from tests.mo.test__shared import valid_org_unit_level
from tests.mo.test__shared import valid_org_unit_type
from tests.mo.test__shared import valid_parent
from tests.mo.test__shared import valid_validity

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestOrganisationUnit:
    @given(
        st.text().filter(lambda s: s != "org_unit"),
        st.text(),
        valid_validity(),
        st.text(),
        valid_parent(),
        valid_org_unit_hier(),
        valid_org_unit_type(),
        valid_org_unit_level(),
    )
    def test_init(
        self,
        type,
        user_key,
        validity,
        name,
        parent,
        org_unit_hier,
        org_unit_type,
        org_unit_level,
    ):
        # Required
        assert OrganisationUnit(
            user_key=user_key,
            validity=validity,
            name=name,
            org_unit_type=org_unit_type,
            org_unit_level=org_unit_level,
        )

        # Optional
        assert OrganisationUnit(
            user_key=user_key,
            validity=validity,
            name=name,
            parent=parent,
            org_unit_hierarchy=org_unit_hier,
            org_unit_type=org_unit_type,
            org_unit_level=org_unit_level,
        )

        # type value error
        with pytest.raises(ValidationError, match="unexpected value;"):
            OrganisationUnit(
                type=type,
                user_key=user_key,
                validity=validity,
                name=name,
                org_unit_type=org_unit_type,
                org_unit_level=org_unit_level,
            )

    @given(
        st.uuids(),
        st.text(),
        st.text(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        valid_dt_range(),
    )
    def test_from_simplified_fields(
        self,
        uuid,
        user_key,
        name,
        org_unit_type_uuid,
        org_unit_level_uuid,
        parent_uuid,
        org_unit_hierarchy_uuid,
        valid_dts,
    ):
        # Required
        assert OrganisationUnit.from_simplified_fields(
            uuid, user_key, name, org_unit_type_uuid, org_unit_level_uuid
        )

        # Optional
        from_dt, to_dt = valid_dts
        assert OrganisationUnit.from_simplified_fields(
            uuid,
            user_key,
            name,
            org_unit_type_uuid,
            org_unit_level_uuid,
            parent_uuid,
            org_unit_hierarchy_uuid,
            from_dt,
            to_dt,
        )
