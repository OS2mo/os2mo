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

from ramodels.mo.engagement import Engagement
from ramodels.mo.engagement import EngagementAssociation
from tests.conftest import valid_dt_range
from tests.mo.test__shared import valid_eng
from tests.mo.test__shared import valid_eng_assoc_type
from tests.mo.test__shared import valid_eng_type
from tests.mo.test__shared import valid_job_fun
from tests.mo.test__shared import valid_org_unit
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_primary
from tests.mo.test__shared import valid_validity

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestEngagement:
    @given(
        st.text().filter(lambda s: s != "engagement"),
        valid_org_unit(),
        valid_pers(),
        valid_job_fun(),
        valid_eng_type(),
        valid_validity(),
        valid_primary(),
        st.text(),
    )
    def test_init(
        self,
        type,
        org_unit,
        person,
        job_function,
        engagement_type,
        validity,
        primary,
        user_key,
    ):
        # Required
        assert Engagement(
            org_unit=org_unit,
            person=person,
            job_function=job_function,
            engagement_type=engagement_type,
            validity=validity,
            primary=primary,
            user_key=user_key,
        )

        # Optional
        # Extensions 1 through 10 are optional, and currently not tested properly.

        # type value error
        with pytest.raises(ValidationError, match="unexpected value;"):
            Engagement(
                type=type,
                org_unit=org_unit,
                person=person,
                job_function=job_function,
                engagement_type=engagement_type,
                validity=validity,
                primary=primary,
                user_key=user_key,
            )

    @given(
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        st.uuids(),
        valid_dt_range(),
        st.uuids(),
        st.text(),
    )
    def test_from_simplified_fields(
        self,
        uuid,
        org_unit,
        person,
        job_function,
        engagement_type,
        valid_dts,
        primary,
        user_key,
    ):
        from_dt, to_dt = valid_dts
        assert Engagement.from_simplified_fields(
            uuid,
            org_unit,
            person,
            job_function,
            engagement_type,
            from_dt,
            to_dt,
            primary,
            user_key,
        )


class TestEngagementAssociation:
    @given(
        st.text().filter(lambda s: s != "engagement_association"),
        valid_org_unit(),
        valid_eng(),
        valid_eng_assoc_type(),
        valid_validity(),
    )
    def test_init(self, type, org_unit, engagement, engagement_assoc, validity):
        assert EngagementAssociation(
            org_unit=org_unit,
            engagement=engagement,
            engagement_association_type=engagement_assoc,
            validity=validity,
        )

        with pytest.raises(ValidationError, match="unexpected value;"):
            EngagementAssociation(
                type=type,
                org_unit=org_unit,
                engagement=engagement,
                engagement_association_type=engagement_assoc,
                validity=validity,
            )

    @given(st.uuids(), st.uuids(), st.uuids(), st.uuids(), valid_dt_range())
    def test_from_simplified_fields(
        self, uuid, org_unit_uuid, engagement_uuid, engagement_assoc_uuid, valid_dts
    ):
        # Required
        assert EngagementAssociation.from_simplified_fields(
            uuid, org_unit_uuid, engagement_uuid, engagement_assoc_uuid
        )

        # Optional
        from_dt, to_dt = valid_dts
        assert EngagementAssociation.from_simplified_fields(
            uuid, org_unit_uuid, engagement_uuid, engagement_assoc_uuid, from_dt, to_dt
        )
