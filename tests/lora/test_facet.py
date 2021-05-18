#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
from uuid import UUID

from ramodels.lora import Facet
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import FacetAttributes
from ramodels.lora._shared import FacetProperties
from ramodels.lora._shared import FacetRelations
from ramodels.lora._shared import FacetStates
from ramodels.lora._shared import InfiniteDatetime
from ramodels.lora._shared import Published
from ramodels.lora._shared import Responsible

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFacet:
    def test_required_fields(self):
        effective_time = EffectiveTime(
            from_date=InfiniteDatetime(datetime.datetime.now()),
            to_date=InfiniteDatetime("infinity"),
        )

        assert Facet(
            uuid=None,
            attributes=FacetAttributes(
                properties=[
                    FacetProperties(user_key="asd", effective_time=effective_time)
                ]
            ),
            states=FacetStates(
                published_state=[Published(effective_time=effective_time)]
            ),
            relations=FacetRelations(
                responsible=[
                    Responsible(
                        uuid="c4ec1247-d040-45ca-8092-61a0aeca9b30",
                        effective_time=effective_time,
                    )
                ]
            ),
        )

    def test_optional_fields(self):
        effective_time = EffectiveTime(
            from_date=InfiniteDatetime(datetime.datetime.now()),
            to_date=InfiniteDatetime("infinity"),
        )

        assert Facet(
            uuid=UUID("92b1d654-f4c5-4fdd-aeb7-73b9b674e91e"),
            attributes=FacetAttributes(
                properties=[
                    FacetProperties(user_key="userkey", effective_time=effective_time)
                ]
            ),
            states=FacetStates(
                published_state=[Published(effective_time=effective_time)]
            ),
            relations=FacetRelations(
                responsible=[
                    Responsible(
                        uuid="c4ec1247-d040-45ca-8092-61a0aeca9b30",
                        effective_time=effective_time,
                    )
                ]
            ),
        )
