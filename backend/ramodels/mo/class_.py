# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from ramodels.mo._shared import MOBase
from ramodels.mo._shared import OpenValidity


class ClassBase(MOBase):
    """A MO class base object."""

    # uuid and user_key is inherited from MOBase

    # type is always "class"
    type_: str = Field("class", alias="type", description="The object type")

    # Required
    validity: OpenValidity = Field(description="Validity of the facet.")

    # These are always Optional:
    scope: str | None = Field(description="Scope of the class.")
    published: str = Field(description="Published state of the class object.")
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")
    org_uuid: UUID | None = Field(None, description="UUID of the related organisation.")


class ClassRead(ClassBase):
    """A MO Class read object."""

    name: str = Field(description="Name/title of the class.")
    facet_uuid: UUID = Field(description="UUID of the related facet.")
    # org_uuid: UUID = Field(description="UUID of the related organisation.")


class ClassWrite(ClassBase):

    """A MO Class write object."""

    name: str = Field(description="Mo-class name.")
    facet_uuid: UUID | None = Field(description="UUID of the related facet.")
    # org_uuid: UUID = Field(description="UUID of the related organisation.")
