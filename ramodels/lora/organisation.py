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

from ._shared import Authority
from ._shared import EffectiveTime
from ._shared import LoraBase
from ._shared import OrganisationAttributes
from ._shared import OrganisationProperties
from ._shared import OrganisationRelations
from ._shared import OrganisationStates
from ._shared import OrganisationValidState


# --------------------------------------------------------------------------------------
# Organisation model
# --------------------------------------------------------------------------------------


class Organisation(LoraBase):
    """
    Attributes:
        attributes:
        states:
        relations:
    """

    attributes: OrganisationAttributes = Field(alias="attributter")
    states: OrganisationStates = Field(alias="tilstande")
    relations: Optional[OrganisationRelations] = Field(alias="relationer")

    # TODO: This should be done with validators setting dynamic fields instead
    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        name: str,
        user_key: str,  # often == name,
        municipality_code: Optional[int] = None,
        from_date: str = "-infinity",
        to_date: str = "infinity",
    ) -> "Organisation":
        # Inner fields
        _effective_time = EffectiveTime(from_date=from_date, to_date=to_date)
        _properties = OrganisationProperties(
            user_key=user_key, name=name, effective_time=_effective_time
        )
        _valid_state = OrganisationValidState(effective_time=_effective_time)
        _authority = None
        if municipality_code:
            _authority = Authority(
                urn=f"urn:dk:kommune:{municipality_code}",
                effective_time=_effective_time,
            )

        # Organisation fields
        attributes = OrganisationAttributes(properties=[_properties])
        states = OrganisationStates(valid_state=[_valid_state])
        relations: Optional[OrganisationRelations] = (
            OrganisationRelations(authority=[_authority]) if _authority else None
        )

        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
