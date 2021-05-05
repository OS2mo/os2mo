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

from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class Validity(RABase):
    from_date: str = Field("1930-01-01", alias="from")
    to_date: Optional[str] = Field(None, alias="to")


class Person(RABase):
    uuid: UUID


class OrgUnitRef(RABase):
    uuid: UUID


class EngagementRef(RABase):
    uuid: UUID
