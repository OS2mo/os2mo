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

from ramodels.lora import Klasse
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import FacetRef
from ramodels.lora._shared import InfiniteDatetime
from ramodels.lora._shared import KlasseAttributes
from ramodels.lora._shared import KlasseProperties
from ramodels.lora._shared import KlasseRelations
from ramodels.lora._shared import KlasseStates
from ramodels.lora._shared import Published
from ramodels.lora._shared import Responsible


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestKlasse:
    def test_required_fields(self):
        effective_time = EffectiveTime(
            from_date=InfiniteDatetime(datetime.datetime.now()),
            to_date=InfiniteDatetime("infinity"),
        )

        properties = KlasseProperties(
            user_key="userkey",
            title="Title",
            effective_time=effective_time,
        )

        attributes = KlasseAttributes(properties=[properties])

        published = Published(effective_time=effective_time)

        states = KlasseStates(published_state=[published])

        responsible = Responsible(
            uuid=uuid4(),
            effective_time=effective_time,
        )

        facet = FacetRef(
            uuid=uuid4(),
            effective_time=effective_time,
        )

        relations = KlasseRelations(responsible=[responsible], facet=[facet])

        klasse = Klasse(attributes=attributes, states=states, relations=relations)

        assert effective_time
        assert properties
        assert attributes
        assert published
        assert states
        assert responsible
        assert facet
        assert relations
        assert klasse

    def test_optional_fields(self):
        effective_time = EffectiveTime(
            from_date=InfiniteDatetime(datetime.datetime.now()),
            to_date=InfiniteDatetime("infinity"),
        )

        # Since the only field that is optional in Klasse is inside
        # KlasseProperties, we only asser KlasseProperties
        assert KlasseProperties(
            user_key="userkey",
            title="Title",
            scope="Text",
            effective_time=effective_time,
        )
