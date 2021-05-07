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
        date_from: str = "1930-01-01",
        date_to: str = "infinity",
    ):
        effective_time = EffectiveTime(from_date=date_from, to_date=date_to)
        attributes = OrganisationAttributes(
            properties=[
                OrganisationProperties(
                    user_key=user_key, name=name, effective_time=effective_time
                )
            ]
        )
        states = OrganisationStates(
            valid_state=[OrganisationValidState(effective_time=effective_time)]
        )

        relations = None
        if municipality_code:
            relations = OrganisationRelations(
                authority=[
                    Authority(
                        urn=f"urn:dk:kommune:{municipality_code}",
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
