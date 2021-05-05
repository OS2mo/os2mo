#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Literal
from uuid import UUID

from pydantic import Field

from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class EffectiveTime(RABase):
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")


class Published(RABase):
    published: str = Field("Publiceret", alias="publiceret")
    effective_time: EffectiveTime = Field(alias="virkning")


class Responsible(RABase):
    object_type: Literal["organisation"] = Field("organisation", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")
