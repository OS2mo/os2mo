# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic import validator

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

    @validator("parent_uuid", pre=True)
    def empty_string_is_none(cls, value: Any) -> Any:
        """Convert UUID-or-empty-string type back to a proper optional UUID type.

        MO models an empty parent by None (sane), but LoRa represents it by the
        empty string (insane)."""
        if value == "":
            return None
        return value
