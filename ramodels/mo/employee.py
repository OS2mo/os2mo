#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Literal
from typing import Optional
from uuid import UUID

from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------


class Employee(RABase):
    type: Literal["employee"] = "employee"
    uuid: UUID
    name: str
    cpr_no: Optional[str] = None
    seniority: Optional[str] = None
