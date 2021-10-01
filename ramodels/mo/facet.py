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

# --------------------------------------------------------------------------------------
# Facet models
# --------------------------------------------------------------------------------------


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
