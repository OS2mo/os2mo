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
        from_date: str = "1930-01-01",
        to_date: str = "infinity",
    ):
        # Inner fields
        _effective_time = EffectiveTime(from_date=from_date, to_date=to_date)
        _properties = KlasseProperties(
            user_key=user_key,
            title=title,
            scope=scope,
            effective_time=_effective_time,
        )
        _published = Published(effective_time=_effective_time)
        _responsible = Responsible(
            uuid=organisation_uuid,
            effective_time=_effective_time,
        )
        _facet = FacetRef(
            uuid=facet_uuid,
            effective_time=_effective_time,
        )

        # Klasse fields
        attributes = KlasseAttributes(properties=[_properties])
        states = KlasseStates(published_state=[_published])
        relations = KlasseRelations(responsible=[_responsible], facet=[_facet])

        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
