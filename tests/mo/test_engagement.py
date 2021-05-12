#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

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
            type="engagement",
            org_unit=OrgUnitRef(uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")),
            person=PersonRef(uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")),
            job_function=JobFunction(uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")),
            engagement_type=EngagementType(
                uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")
            ),
            validity=Validity(from_date="1930-01-01", to_date=None),
            primary=Primary(uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")),
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
