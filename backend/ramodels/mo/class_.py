#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Optional
from uuid import UUID

from pydantic import Field

from ramodels.mo._shared import MOBase

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class ClassBase(MOBase):
    """A MO class base object."""

    # uuid and user_key is inherited from MOBase

    # type is always "class"
    type_: str = Field("class", alias="type", description="The object type")
    # These are always Optional:
    scope: Optional[str] = Field(description="Scope of the class.")
    published: Optional[str] = Field(description="Published state of the class object.")
    parent_uuid: Optional[UUID] = Field(description="UUID of the parent class.")
    example: Optional[str] = Field(description="Example usage.")
    owner: Optional[UUID] = Field(description="Owner of class")


class ClassRead(ClassBase):
    """A MO Class read object."""

    name: str = Field(description="Name/title of the class.")
    facet_uuid: UUID = Field(description="UUID of the related facet.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")


class ClassWrite(ClassBase):

    """A MO Class write object."""

    name: str = Field(description="Mo-class name.")
    facet_uuid: Optional[UUID] = Field(description="UUID of the related facet.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
