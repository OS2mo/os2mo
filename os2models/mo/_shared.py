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

from os2models.base import OS2Base

# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class Validity(OS2Base):
    from_date: str = Field("1930-01-01", alias="from")
    to_date: Optional[str] = Field(None, alias="to")


class Person(OS2Base):
    uuid: UUID


class OrgUnitRef(OS2Base):
    uuid: UUID


class EngagementRef(OS2Base):
    uuid: UUID
