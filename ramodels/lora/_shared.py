#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from uuid import UUID
from uuid import uuid4

from pydantic import Field
from pydantic import validator

from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# LoRaBase
# --------------------------------------------------------------------------------------


class LoraBase(RABase):
    # TODO: This is duplicated to each class that cannot be instantiated.
    # We should probably find a better solution.
    def __new__(cls, *args, **kwargs) -> Any:
        if cls is LoraBase:
            raise TypeError("LoraBase may not be instantiated")
        return super().__new__(cls)

    uuid: UUID = Field(None)

    # Autogenerate UUID if necessary
    # TODO: in pydantic v2, this can be replaced with Field(default_factory=uuid4)
    # However, the beta version of default_factory is still unstable and prone to
    # side-effects.
    @validator("uuid", pre=True, always=True)
    def set_uuid(cls, _uuid: Optional[UUID]) -> UUID:
        return _uuid or uuid4()


# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class EffectiveTime(RABase):
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")


class Authority(RABase):
    urn: str
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetProperties(RABase):
    user_key: str = Field(alias="brugervendtnoegle")
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetAttributes(RABase):
    properties: List[FacetProperties] = Field(
        alias="facetegenskaber", min_items=1, max_items=1
    )


class Published(RABase):
    published: str = Field("Publiceret", alias="publiceret")
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetStates(RABase):
    published_state: List[Published] = Field(
        alias="facetpubliceret", min_items=1, max_items=1
    )


class Responsible(RABase):
    object_type: Literal["organisation"] = Field("organisation", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetRef(RABase):
    object_type: Literal["facet"] = Field("facet", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetRelations(RABase):
    responsible: List[Responsible] = Field(alias="ansvarlig", min_items=1, max_items=1)


class KlasseProperties(RABase):
    user_key: str = Field(alias="brugervendtnoegle")
    title: str = Field(alias="titel")
    scope: Optional[str] = Field(None, alias="omfang")
    effective_time: EffectiveTime = Field(alias="virkning")


class KlasseRelations(RABase):
    responsible: List[Responsible] = Field(alias="ansvarlig")
    facet: List[FacetRef]


class KlasseAttributes(RABase):
    properties: List[KlasseProperties] = Field(
        alias="klasseegenskaber", min_items=1, max_items=1
    )


class KlasseStates(RABase):
    published_state: List[Published] = Field(
        alias="klassepubliceret", min_items=1, max_items=1
    )


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
