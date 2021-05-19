#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import uuid4

from ramodels.mo._shared import EngagementType
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import Validity
from ramodels.mo.engagement import Engagement


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestEngagement:
    def test_required_fields(self):
        assert Engagement(
            org_unit=OrgUnitRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            job_function=JobFunction(uuid=uuid4()),
            engagement_type=EngagementType(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
            primary=Primary(uuid=uuid4()),
            user_key="engagement",
        )

    def test_optional_fiels(self):
        assert Engagement(
            type="engagement",
            org_unit=OrgUnitRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            job_function=JobFunction(uuid=uuid4()),
            engagement_type=EngagementType(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
            primary=Primary(uuid=uuid4()),
            user_key="engagement",
            extension_1="",
            extension_2="",
            extension_3="",
            extension_4="",
            extension_5="",
            extension_6="",
            extension_7="",
            extension_8="",
            extension_9="",
            extension_10="",
        )
