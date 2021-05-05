#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from ._shared import EffectiveTime
from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Organisation implementations
# --------------------------------------------------------------------------------------


class Authority(RABase):
    urn: str
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationProperties(RABase):
    user_key: str = Field(alias="brugervendtnoegle")
    name: str = Field(alias="organisationsnavn")
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationAttributes(RABase):
    properties: List[OrganisationProperties] = Field(
        alias="organisationegenskaber", min_items=1, max_items=1
    )


class OrganisationValidState(RABase):
    state: str = Field("Aktiv", alias="gyldighed")
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationStates(RABase):
    valid_state: List[OrganisationValidState] = Field(
        alias="organisationgyldighed", min_items=1, max_items=1
    )


class OrganisationRelations(RABase):
    authority: List[Authority] = Field(alias="myndighed", min_items=1, max_items=1)


# --------------------------------------------------------------------------------------
# Organisation model
# --------------------------------------------------------------------------------------


class Organisation(RABase):
    attributes: OrganisationAttributes = Field(alias="attributter")
    states: OrganisationStates = Field(alias="tilstande")
    relations: Optional[OrganisationRelations] = Field(alias="relationer")
    # TODO, PENDING: https://github.com/samuelcolvin/pydantic/pull/2231
    # for now, this value is included,
    # and has to be excluded manually when converting to json
    uuid: Optional[UUID] = None  # Field(None, exclude=True)

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
