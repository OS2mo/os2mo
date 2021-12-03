#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from pydantic import Field

from ._shared import MOBase

# --------------------------------------------------------------------------------------
# Organisation model
# --------------------------------------------------------------------------------------


class OrganisationRead(MOBase):
    """A MO organisation object."""

    type_: str = Field("organisation", alias="type", description="The object type")
    name: str = Field(description="Name of the organisation.")
