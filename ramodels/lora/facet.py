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
from ._shared import FacetAttributes
from ._shared import FacetProperties
from ._shared import FacetRelations
from ._shared import FacetStates
from ._shared import LoraBase
from ._shared import Published
from ._shared import RegistrationTime
from ._shared import Responsible


# --------------------------------------------------------------------------------------
# Facet model
# --------------------------------------------------------------------------------------


class Facet(LoraBase):
    """
    A LoRa facet.
    """

    attributes: FacetAttributes = Field(
        alias="attributter", description="The facet attributes."
    )
    states: FacetStates = Field(alias="tilstande", description="The facet states.")
    relations: FacetRelations = Field(
        alias="relationer", description="The facet relations."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        user_key: str,
        organisation_uuid: UUID,
        uuid: Optional[UUID] = None,
        from_date: str = "-infinity",
        to_date: str = "infinity",
    ) -> "Facet":
        "Create a Facet from simplified fields."
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


class FacetRead(Facet):
    from_time: RegistrationTime = Field(
        alias="fratidspunkt", description="The facet registration from time."
    )
    to_time: RegistrationTime = Field(
        alias="tiltidspunkt", description="The facet registration to time."
    )
    life_cycle_code: str = Field(
        alias="livscykluskode", description="The facet registation life cycle code."
    )
    user_ref: UUID = Field(
        alias="brugerref", description="The facet registration user."
    )
