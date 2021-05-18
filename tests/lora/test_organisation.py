#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime

from ramodels.lora import Organisation
from ramodels.lora._shared import Authority
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import InfiniteDatetime
from ramodels.lora._shared import OrganisationAttributes
from ramodels.lora._shared import OrganisationProperties
from ramodels.lora._shared import OrganisationRelations
from ramodels.lora._shared import OrganisationStates
from ramodels.lora._shared import OrganisationValidState


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestOrganisation:
    def test_required_fields(self):
        effective_time = EffectiveTime(
            from_date=InfiniteDatetime(datetime.datetime.now()),
            to_date=InfiniteDatetime("infinity"),
        )

        properties = OrganisationProperties(
            user_key="userkey", name="Name", effective_time=effective_time
        )

        attributes = OrganisationAttributes(properties=[properties])

        valid_state = OrganisationValidState(effective_time=effective_time)

        states = OrganisationStates(valid_state=[valid_state])

        organisation = Organisation(attributes=attributes, states=states)

        assert effective_time
        assert properties
        assert attributes
        assert valid_state
        assert states
        assert organisation

    def test_optional_fields(self):
        effective_time = EffectiveTime(
            from_date=InfiniteDatetime(datetime.datetime.now()),
            to_date=InfiniteDatetime("infinity"),
        )

        assert Organisation(
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
