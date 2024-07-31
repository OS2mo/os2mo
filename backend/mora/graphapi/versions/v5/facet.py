# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from pydantic import Field

from mora.graphapi.gmodels.base import RABase
from mora.graphapi.gmodels.lora._shared import EffectiveTime
from mora.graphapi.gmodels.lora._shared import LoraBase


class FacetProperties(RABase):
    """
    Properties of a given LoRa facet.
    """

    user_key: str = Field(alias="brugervendtnoegle", description="Short, unique key.")
    description: str | None = Field(
        alias="beskrivelse", description="The facet description."
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the property."
    )


class FacetAttributes(RABase):
    """
    Attributes of a given LoRa facet.
    """

    properties: list[FacetProperties] = Field(
        alias="facetegenskaber",
        min_items=1,
        max_items=1,
        description="The facet property denoting the attributes.",
    )


class Published(RABase):
    """
    Published state of a given object in LoRa.
    """

    # TODO: published are actually Enums in LoRa, but it's currently not possible
    # to lift them from LoRa systematically. We should definitely fix this!

    published: str = Field(
        "Publiceret",
        alias="publiceret",
        description="String representing the published status.",
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="The effective time of the states."
    )


class FacetStates(RABase):
    """
    States of a given LoRa facet.
    """

    published_state: list[Published] = Field(
        alias="facetpubliceret",
        min_items=1,
        max_items=1,
        description="The published state of the facet.",
    )


class Responsible(LoraBase):
    """
    Responsible object in LoRa.
    """

    object_type: Literal["organisation"] = Field(
        "organisation", alias="objekttype", description="Object type."
    )
    uuid: UUID = Field(description="UUID of the object.")
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the object."
    )


class ParentClassification(LoraBase):
    """
    ParentClassification object in LoRa.
    """

    object_type: Literal["klassifikation"] = Field(
        "klassifikation", alias="objekttype", description="Object type."
    )
    uuid: UUID = Field(description="UUID of the object.")
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the object."
    )


class FacetRelations(RABase):
    """
    Facet relations given by responsible objects.
    """

    responsible: list[Responsible] = Field(
        alias="ansvarlig",
        min_items=1,
        max_items=1,
        description="The responsible object.",
    )
    parent: list[ParentClassification] | None = Field(
        alias="facettilhoerer",
        min_items=1,
        max_items=1,
        description="The parent classification.",
    )


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
        uuid: UUID | None = None,
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
