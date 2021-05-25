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

from ramodels.mo.address import Address
from tests.conftest import valid_dt_range
from tests.mo.test__shared import valid_addr_type
from tests.mo.test__shared import valid_eng
from tests.mo.test__shared import valid_org_ref
from tests.mo.test__shared import valid_org_unit
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_validity
from tests.mo.test__shared import valid_vis

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


class TestAddress:
    @given(
        st.text().filter(lambda s: s != "address"),
        st.text(),
        st.text(),
        valid_addr_type(),
        valid_org_ref(),
        valid_pers(),
        valid_org_unit(),
        valid_eng(),
        valid_validity(),
        valid_vis(),
    )
    def test_init(
        self,
        type,
        value,
        value2,
        addr_type,
        org_ref,
        person,
        org_unit,
        eng,
        validity,
        visibility,
    ):
        # Required
        assert Address(
            value=value, address_type=addr_type, org=org_ref, validity=validity
        )
        # Optional
        assert Address(
            value=value,
            value2=value2,
            address_type=addr_type,
            org=org_ref,
            person=person,
            org_unit=org_unit,
            engagement=eng,
            validity=validity,
            visibility=visibility,
        )
        # type value error
        with pytest.raises(ValidationError, match="unexpected value;"):
            Address(
                type=type,
                value=value,
                address_type=addr_type,
                org=org_ref,
                validity=validity,
            )

    @given(
        st.uuids(),
        st.text(),
        st.uuids(),
        st.uuids(),
        valid_dt_range(),
        st.text(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
    )
    def test_from_simplified_fields(
        self,
        uuid,
        value,
        addr_type_uuid,
        org_uuid,
        valid_dts,
        value2,
        person_uuid,
        org_unit_uuid,
        engagement_uuid,
        visibility_uuid,
    ):
        from_dt, to_dt = valid_dts
        # Required
        assert Address.from_simplified_fields(
            uuid, value, addr_type_uuid, org_uuid, from_dt
        )

        # Optional
        assert Address.from_simplified_fields(
            uuid,
            value,
            addr_type_uuid,
            org_uuid,
            from_dt,
            to_dt,
            value2,
            person_uuid,
            org_unit_uuid,
            engagement_uuid,
            visibility_uuid,
        )
