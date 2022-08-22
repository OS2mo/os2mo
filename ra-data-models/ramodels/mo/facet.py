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
from ramodels.mo._shared import MOBase

from ._shared import AlphaStr

# --------------------------------------------------------------------------------------
# Facet models
# --------------------------------------------------------------------------------------


class FacetRead(MOBase):
    """A MO Facet read object."""

    type_: str = Field("facet", alias="type", description="The object type")
    user_key: str = Field(description="Short, unique key.")
    published: Optional[str] = Field(description="Published state of the facet object.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
    parent_uuid: Optional[UUID] = Field(description="UUID of the parent facet.")
    description: str = Field(description="Description of the facet object.", default="")


class FacetWrite(MOBase):
    """A MO Facet write object."""

    type_: str = Field("facet", alias="type", description="The object type")
    description: AlphaStr = Field(description="Description of the facet object.")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
    user_key: str = Field(description="Short, unique key.")
    published: Optional[str] = Field(description="Published state of the facet object.")
    parent_uuid: Optional[UUID] = Field(description="UUID of the parent facet.")


class FacetClass(MOBase):
    """Payload model for Klasses to be created under the given Facet."""

    facet_uuid: UUID = Field(
        description="UUID of the facet for which the Klasse should be created."
    )
    name: str = Field(description="Name of the Klasse.")
    user_key: str = Field(description="Short, unique key.")
    scope: Optional[str] = Field(description="Scope of the created Klasse.")
    org_uuid: UUID = Field(
        description="UUID of the organisation for which the Klasse should be created."
    )
