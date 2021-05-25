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

from ramodels.mo.association import Association
from tests.conftest import valid_dt_range
from tests.mo.test__shared import valid_assoc_type
from tests.mo.test__shared import valid_org_unit
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_validity


# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


class TestAssociation:
    @given(
        st.text().filter(lambda s: s != "association"),
        valid_org_unit(),
        valid_pers(),
        valid_assoc_type(),
        valid_validity(),
    )
    def test_init(self, type, org_unit, person, assoc_type, validity):
        # Required
        assert Association(
            org_unit=org_unit,
            person=person,
            association_type=assoc_type,
            validity=validity,
        )

        # type value error
        with pytest.raises(ValidationError, match="unexpected value;"):
            Association(
                type=type,
                org_unit=org_unit,
                person=person,
                association_type=assoc_type,
                validity=validity,
            )

    @given(st.uuids(), st.uuids(), st.uuids(), st.uuids(), valid_dt_range())
    def test_from_simplified_fields(
        self, uuid, org_unit_uuid, person_uuid, assoc_type_uuid, valid_dts
    ):
        # Required
        assert Association.from_simplified_fields(
            uuid, org_unit_uuid, person_uuid, assoc_type_uuid
        )

        # Optional
        from_dt, to_dt = valid_dts
        assert Association.from_simplified_fields(
            uuid, org_unit_uuid, person_uuid, assoc_type_uuid, from_dt, to_dt
        )
