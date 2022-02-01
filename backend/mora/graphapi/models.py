#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from pydantic import BaseModel
from pydantic import Field

# --------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------


class SemanticVersionRead(BaseModel):
    major: int
    minor: int
    patch: int


class HealthRead(BaseModel):
    """Payload model for health."""

    identifier: str = Field(description="Short, unique key.")
