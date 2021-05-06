#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any

from pydantic import BaseModel
from pydantic import Extra

# --------------------------------------------------------------------------------------
# Base models
# --------------------------------------------------------------------------------------


class RABase(BaseModel):
    """Base model for RA data models."""

    # TODO: This is duplicated to each class that cannot be instantiated.
    # We should probably find a better solution.
    def __new__(cls, *args, **kwargs) -> Any:
        if cls is RABase:
            raise TypeError("RABase may not be instantiated")
        return super().__new__(cls)

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid
