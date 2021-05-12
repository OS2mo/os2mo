#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from ramodels.lora import Klasse
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import FacetRef
from ramodels.lora._shared import KlasseAttributes
from ramodels.lora._shared import KlasseProperties
from ramodels.lora._shared import KlasseRelations
from ramodels.lora._shared import KlasseStates
from ramodels.lora._shared import Published
from ramodels.lora._shared import Responsible


class TestKlasse:
    def test_required_fields(self):
        effective_time = EffectiveTime(from_date="1930-01-01", to_date="Infinity")
        test_klasse = Klasse(
            uuid=None,
            attributes=KlasseAttributes(
                properties=[
                    KlasseProperties(
                        user_key="userkey",
                        title="Title",
                        scope=None,
                        effective_time=effective_time,
                    )
                ]
            ),
            states=KlasseStates(
                published_state=[Published(effective_time=effective_time)]
            ),
            relations=KlasseRelations(
                responsible=[
                    Responsible(
                        uuid=UUID("27fc3b84-aa3d-4702-bf8e-3c24cbeaac29"),
                        effective_time=effective_time,
                    )
                ],
                facet=[
                    FacetRef(
                        uuid=UUID("f922c1c5-33c5-4bc9-903a-4c703bbc872d"),
                        effective_time=effective_time,
                    )
                ],
            ),
        )
        assert test_klasse

    def test_optional_fields(self):
        effective_time = EffectiveTime(from_date="1930-01-01", to_date="Infinity")
        test_klasse = Klasse(
            uuid=UUID("92b1d654-f4c5-4fdd-aeb7-73b9b674e91e"),
            attributes=KlasseAttributes(
                properties=[
                    KlasseProperties(
                        user_key="userkey",
                        title="Title",
                        scope="text",
                        effective_time=effective_time,
                    )
                ]
            ),
            states=KlasseStates(
                published_state=[Published(effective_time=effective_time)]
            ),
            relations=KlasseRelations(
                responsible=[
                    Responsible(
                        uuid=UUID("27fc3b84-aa3d-4702-bf8e-3c24cbeaac29"),
                        effective_time=effective_time,
                    )
                ],
                facet=[
                    FacetRef(
                        uuid=UUID("f922c1c5-33c5-4bc9-903a-4c703bbc872d"),
                        effective_time=effective_time,
                    )
                ],
            ),
        )
        assert test_klasse
