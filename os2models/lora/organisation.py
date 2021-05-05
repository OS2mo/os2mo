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
from os2models.base import OS2Base

# --------------------------------------------------------------------------------------
# Organisation implementations
# --------------------------------------------------------------------------------------


class Authority(OS2Base):
    urn: str
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationProperties(OS2Base):
    user_key: str = Field(alias="brugervendtnoegle")
    name: str = Field(alias="organisationsnavn")
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationAttributes(OS2Base):
    properties: List[OrganisationProperties] = Field(
        alias="organisationegenskaber", min_items=1, max_items=1
    )


class OrganisationValidState(OS2Base):
    state: str = Field("Aktiv", alias="gyldighed")
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationStates(OS2Base):
    valid_state: List[OrganisationValidState] = Field(
        alias="organisationgyldighed", min_items=1, max_items=1
    )


class OrganisationRelations(OS2Base):
    authority: List[Authority] = Field(alias="myndighed", min_items=1, max_items=1)


# --------------------------------------------------------------------------------------
# Organisation model
# --------------------------------------------------------------------------------------


class Organisation(OS2Base):
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
