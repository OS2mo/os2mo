# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from mora.graphapi.gmodels.mo._shared import MOBase


class ClassRead(MOBase):
    """A MO Class read object."""

    # uuid and user_key is inherited from MOBase

    # type is always "class"
    type_: str = Field("class", alias="type", description="The object type")
    # These are always Optional:
    scope: str | None = Field(description="Scope of the class.")
    published: str | None = Field(description="Published state of the class object.")
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")
    description: str | None = Field(description="Description of the class object.")

    name: str = Field(description="Name/title of the class.")
    facet_uuid: UUID = Field(description="UUID of the related facet.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
