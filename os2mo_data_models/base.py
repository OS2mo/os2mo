#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from pydantic import BaseModel
from pydantic import Extra

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class OS2Base(BaseModel):
    """Base model for OS2 data models."""

    class Config:
        allow_mutation = False
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid
