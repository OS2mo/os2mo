# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Optional
from uuid import UUID

from ramodels.mo._shared import MOBase
from pydantic import BaseModel
from pydantic import Field


class ClassRead(MOBase):
    """Payload model for classes to be created under the given facet."""

    type_: str = Field("class", alias="type", description="The object type")
    name: str = Field(description="Name/titel of the class.")
    user_key: str = Field(description="Short, unique key.")
    scope: Optional[str] = Field(description="Scope of the created class.")

    published: Optional[str] = Field(description="Published state of the class object.")

    facet_uuid: UUID = Field(
        description="UUID of the facet for which the class should be created."
    )
    org_uuid: UUID = Field(
        description="UUID of the organisation for which the class should be created."
    )
    parent_uuid: Optional[UUID] = Field(description="UUID of the parent class.")


class FacetRead(MOBase):
    """Payload model for facets."""

    type_: str = Field("facet", alias="type", description="The object type")
    user_key: str = Field(description="Short, unique key.")

    published: Optional[str] = Field(description="Published state of the class object.")

    org_uuid: UUID = Field(
        description="UUID of the organisation for which is responsible."
    )
    parent_uuid: Optional[UUID] = Field(
        description="UUID of the parent classification."
    )


class SemanticVersion(BaseModel):
    major: int
    minor: int
    patch: int
