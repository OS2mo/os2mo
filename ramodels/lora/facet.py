#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import List
from typing import Literal
from typing import Optional
from uuid import UUID

from pydantic import Field

from ._shared import EffectiveTime
from ._shared import Published
from ._shared import Responsible
from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Facet implementations
# --------------------------------------------------------------------------------------


class FacetProperties(RABase):
    user_key: str = Field(alias="brugervendtnoegle")
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetAttributes(RABase):
    properties: List[FacetProperties] = Field(
        alias="facetegenskaber", min_items=1, max_items=1
    )


class FacetStates(RABase):
    published_state: List[Published] = Field(
        alias="facetpubliceret", min_items=1, max_items=1
    )


class FacetRelations(RABase):
    responsible: List[Responsible] = Field(alias="ansvarlig", min_items=1, max_items=1)


class FacetRef(RABase):
    object_type: Literal["facet"] = Field("facet", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")


# --------------------------------------------------------------------------------------
# Facet model
# --------------------------------------------------------------------------------------


class Facet(RABase):
    attributes: FacetAttributes = Field(alias="attributter")
    states: FacetStates = Field(alias="tilstande")
    relations: FacetRelations = Field(alias="relationer")
    # TODO, PENDING: https://github.com/samuelcolvin/pydantic/pull/2231
    # for now, this value is included, and has to be excluded when converted to json
    uuid: Optional[UUID] = None  # Field(None, exclude=True)

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
