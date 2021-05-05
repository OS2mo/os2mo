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
from ._shared import Published
from ._shared import Responsible
from .facet import FacetRef
from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Klasse implementations
# --------------------------------------------------------------------------------------


class KlasseProperties(RABase):
    user_key: str = Field(alias="brugervendtnoegle")
    title: str
    scope: Optional[str] = Field(None, alias="omfang")
    effective_time: EffectiveTime = Field(alias="virkning")


class KlasseAttributes(RABase):
    properties: List[KlasseProperties] = Field(
        alias="klasseegenskaber", min_items=1, max_items=1
    )


class KlasseStates(RABase):
    published_state: List[Published] = Field(
        alias="klassepubliceret", min_items=1, max_items=1
    )


# --------------------------------------------------------------------------------------
# Klasse implementations
# --------------------------------------------------------------------------------------


class KlasseRelations(RABase):
    responsible: List[Responsible] = Field(alias="ansvarlig")
    facet: List[FacetRef] = Field(alias="ansvarlig")


class Klasse(RABase):
    attributes: KlasseAttributes = Field(alias="attributter")
    states: KlasseStates = Field(alias="tilstande")
    relations: KlasseRelations = Field(alias="relationer")
    # TODO, PENDING: https://github.com/samuelcolvin/pydantic/pull/2231
    # for now, this value is included, and has to be excluded when converted to json
    uuid: Optional[UUID] = None  # Field(None, exclude=True)

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
