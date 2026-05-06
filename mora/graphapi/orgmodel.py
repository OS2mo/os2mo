# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL org related helper functions."""

from uuid import UUID

from pydantic import Field

from mora.graphapi.gmodels.base import RABase
from mora.graphapi.gmodels.lora._shared import EffectiveTime
from mora.graphapi.gmodels.lora._shared import LoraBase


class Authority(RABase):
    """Authority as given by URN."""

    urn: str = Field(
        regex=r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$",
        description="URN of the authority.",
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the authority."
    )


class OrganisationProperties(RABase):
    """
    LoRa organisation properties.
    """

    user_key: str = Field(alias="brugervendtnoegle", description="Short, unique key.")
    name: str = Field(
        alias="organisationsnavn", description="Name of the organisation."
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the properties."
    )


class OrganisationAttributes(RABase):
    """
    LoRa organisation attributes.
    """

    properties: list[OrganisationProperties] = Field(
        alias="organisationegenskaber",
        min_items=1,
        max_items=1,
        description="Properties denoting the attributes.",
    )


class OrganisationValidState(RABase):
    """
    State of an organisation in LoRa.
    """

    state: str = Field(
        "Aktiv",
        alias="gyldighed",
        description="String describing the validity of an organisation.",
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the valid states."
    )


class OrganisationStates(RABase):
    """
    Organisation validity as given by OrganisationValidState.
    """

    valid_state: list[OrganisationValidState] = Field(
        alias="organisationgyldighed",
        min_items=1,
        max_items=1,
        description="Valid states denoting the overall state.",
    )


class OrganisationRelations(RABase):
    """
    Organisation relations given by an authority object.
    """

    authority: list[Authority] = Field(
        alias="myndighed",
        min_items=1,
        max_items=1,
        description="Authority object denoting the relations.",
    )


class Organisation(LoraBase):
    """
    A LoRa organisation.
    """

    attributes: OrganisationAttributes = Field(
        alias="attributter", description="The organisation attributes."
    )
    states: OrganisationStates = Field(
        alias="tilstande", description="The organisation states."
    )
    relations: OrganisationRelations | None = Field(
        alias="relationer", description="The organisation relations."
    )

    # TODO: This should be done with validators setting dynamic fields instead
    @classmethod
    def from_simplified_fields(
        cls,
        name: str,
        user_key: str,  # often == name,
        uuid: UUID | None = None,
        municipality_code: int | None = None,
        from_date: str = "-infinity",
        to_date: str = "infinity",
    ) -> "Organisation":
        "Create an organisation from simplified fields."
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
        relations: OrganisationRelations | None = (
            OrganisationRelations(authority=[_authority]) if _authority else None
        )

        return cls(
            attributes=attributes,
            states=states,
            relations=relations,
            uuid=uuid,
        )
