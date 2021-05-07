#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Optional
from uuid import UUID

from pydantic import Field

from ._shared import EffectiveTime
from ._shared import FacetRef
from ._shared import KlasseAttributes
from ._shared import KlasseProperties
from ._shared import KlasseRelations
from ._shared import KlasseStates
from ._shared import LoraBase
from ._shared import Published
from ._shared import Responsible


# --------------------------------------------------------------------------------------
# Klasse model
# --------------------------------------------------------------------------------------


class Klasse(LoraBase):
    attributes: KlasseAttributes = Field(alias="attributter")
    states: KlasseStates = Field(alias="tilstande")
    relations: KlasseRelations = Field(alias="relationer")

    @classmethod
    def from_simplified_fields(
        cls,
        facet_uuid: UUID,  # uuid
        uuid: UUID,
        user_key: str,  # rarely used
        scope: Optional[str],
        organisation_uuid: UUID,
        title: str,
        date_from: str = "1930-01-01",
        date_to: str = "infinity",
    ):
        effective_time = EffectiveTime(from_date=date_from, to_date=date_to)
        attributes = KlasseAttributes(
            properties=[
                KlasseProperties(
                    user_key=user_key,
                    title=title,
                    scope=scope,
                    effective_time=effective_time,
                )
            ]
        )
        states = KlasseStates(
            published_state=[Published(effective_time=effective_time)]
        )

        relations = KlasseRelations(
            responsible=[
                Responsible(
                    uuid=organisation_uuid,
                    effective_time=effective_time,
                )
            ],
            facet=[
                FacetRef(
                    uuid=facet_uuid,
                    effective_time=effective_time,
                )
            ],
        )
        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
