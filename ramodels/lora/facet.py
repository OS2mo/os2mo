#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from pydantic import Field

from ._shared import EffectiveTime
from ._shared import FacetAttributes
from ._shared import FacetProperties
from ._shared import FacetRelations
from ._shared import FacetStates
from ._shared import LoraBase
from ._shared import Published
from ._shared import Responsible


# --------------------------------------------------------------------------------------
# Facet model
# --------------------------------------------------------------------------------------


class Facet(LoraBase):
    attributes: FacetAttributes = Field(alias="attributter")
    states: FacetStates = Field(alias="tilstande")
    relations: FacetRelations = Field(alias="relationer")

    # TODO: This should be done with validators setting dynamic fields instead
    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        user_key: str,
        organisation_uuid: UUID,
        date_from: str = "1930-01-01",
        date_to: str = "infinity",
    ):
        effective_time = EffectiveTime(from_date=date_from, to_date=date_to)
        attributes = FacetAttributes(
            properties=[
                FacetProperties(user_key=user_key, effective_time=effective_time)
            ]
        )
        states = FacetStates(published_state=[Published(effective_time=effective_time)])

        relations = FacetRelations(
            responsible=[
                Responsible(
                    uuid=organisation_uuid,
                    effective_time=effective_time,
                )
            ]
        )
        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
