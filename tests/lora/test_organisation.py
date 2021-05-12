#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from ramodels.lora import Organisation
from ramodels.lora._shared import Authority
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import OrganisationAttributes
from ramodels.lora._shared import OrganisationProperties
from ramodels.lora._shared import OrganisationRelations
from ramodels.lora._shared import OrganisationStates
from ramodels.lora._shared import OrganisationValidState


class TestOrganisation:
    def test_required_fields(self):
        effective_time = EffectiveTime(from_date="1930-01-01", to_date="Infinity")
        test_organisation = Organisation(
            uuid=None,
            attributes=OrganisationAttributes(
                properties=[
                    OrganisationProperties(
                        user_key="userkey", name="Name", effective_time=effective_time
                    )
                ]
            ),
            states=OrganisationStates(
                valid_state=[OrganisationValidState(effective_time=effective_time)]
            ),
            relations=None,
        )
        assert test_organisation

    def test_optional_fields(self):
        effective_time = EffectiveTime(from_date="1930-01-01", to_date="Infinity")

        test_organisation = Organisation(
            uuid=UUID("92b1d654-f4c5-4fdd-aeb7-73b9b674e91e"),
            attributes=OrganisationAttributes(
                properties=[
                    OrganisationProperties(
                        user_key="userkey", name="Name", effective_time=effective_time
                    )
                ]
            ),
            states=OrganisationStates(
                valid_state=[OrganisationValidState(effective_time=effective_time)]
            ),
            relations=OrganisationRelations(
                authority=[
                    Authority(
                        urn=f"urn:dk:kommune:{'municity code'}",
                        effective_time=effective_time,
                    )
                ]
            ),
        )
        assert test_organisation
