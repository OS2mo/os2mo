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
    """
    Attributes:
        attributes:
        states:
        relations:
    """

    attributes: FacetAttributes = Field(alias="attributter")
    states: FacetStates = Field(alias="tilstande")
    relations: FacetRelations = Field(alias="relationer")

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        user_key: str,
        organisation_uuid: UUID,
        from_date: str = "-infinity",
        to_date: str = "infinity",
    ) -> "Facet":
        # Inner fields
        _effective_time = EffectiveTime(from_date=from_date, to_date=to_date)
        _properties = FacetProperties(user_key=user_key, effective_time=_effective_time)
        _published = Published(effective_time=_effective_time)
        _responsible = Responsible(
            uuid=organisation_uuid,
            effective_time=_effective_time,
        )

        # Facet fields
        attributes = FacetAttributes(properties=[_properties])
        states = FacetStates(published_state=[_published])
        relations = FacetRelations(responsible=[_responsible])

        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
