# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from ramodels.mo._shared import MOBase


class FacetRead(MOBase):
    """A MO Facet read object."""

    type_: str = Field("facet", alias="type", description="The object type")
    user_key: str = Field(description="Short, unique key.")
    published: str | None = Field(description="Published state of the facet object.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
    parent_uuid: UUID | None = Field(description="UUID of the parent facet.")
    description: str = Field(description="Description of the facet object.", default="")


class FacetWrite(MOBase):
    """A MO Facet write object."""

    type_: str = Field("facet", alias="type", description="The object type")
    description: str = Field(description="Description of the facet object.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
    user_key: str = Field(description="Short, unique key.")
    published: str | None = Field(description="Published state of the facet object.")
    parent_uuid: UUID | None = Field(description="UUID of the parent facet.")
