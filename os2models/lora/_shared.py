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

from os2models.base import OS2Base

# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class EffectiveTime(OS2Base):
    from_date: str = Field(alias="from")
    to_date: str = Field(alias="to")


class Published(OS2Base):
    published: str = Field("Publiceret", alias="publiceret")
    effective_time: EffectiveTime = Field(alias="virkning")


class Responsible(OS2Base):
    object_type: Literal["organisation"] = Field("organisation", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")
