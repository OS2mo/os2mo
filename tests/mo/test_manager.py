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

from ramodels.mo import Manager
from tests.conftest import valid_dt_range
from tests.mo.test__shared import valid_man_level
from tests.mo.test__shared import valid_man_type
from tests.mo.test__shared import valid_org_unit
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_resp
from tests.mo.test__shared import valid_validity

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestManager:
    @given(
        valid_org_unit(),
        valid_pers(),
        st.lists(valid_resp()),
        valid_man_level(),
        valid_man_type(),
        valid_validity(),
    )
    def test_init(
        self, org_unit, person, responsibility, manager_level, manager_type, validity
    ):
        assert Manager(
            org_unit=org_unit,
            person=person,
            responsibility=responsibility,
            manager_level=manager_level,
            manager_type=manager_type,
            validity=validity,
        )

    @given(
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        valid_dt_range(),
    )
    def test_from_simplified_fields(
        self,
        uuid,
        org_unit_uuid,
        person_uuid,
        resp_uuid,
        man_level_uuid,
        man_type_uuid,
        valid_dts,
    ):
        # Required
        assert Manager.from_simplified_fields(
            uuid, org_unit_uuid, person_uuid, resp_uuid, man_level_uuid, man_type_uuid
        )

        # Optional
        from_dt, to_dt = valid_dts
        assert Manager.from_simplified_fields(
            uuid,
            org_unit_uuid,
            person_uuid,
            resp_uuid,
            man_level_uuid,
            man_type_uuid,
            from_dt,
            to_dt,
        )
