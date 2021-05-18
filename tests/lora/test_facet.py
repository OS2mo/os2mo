#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import datetime
from uuid import uuid4

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

        responsible = Responsible(
            uuid=uuid4(),
            effective_time=effective_time,
        )

        properties = FacetProperties(user_key="asd", effective_time=effective_time)

        attributes = FacetAttributes(properties=[properties])

        published = Published(effective_time=effective_time)

        states = FacetStates(published_state=[published])

        relations = FacetRelations(responsible=[responsible])

        facet = Facet(attributes=attributes, states=states, relations=relations)

        assert effective_time
        assert responsible
        assert properties
        assert attributes
        assert published
        assert states
        assert relations
        assert facet
