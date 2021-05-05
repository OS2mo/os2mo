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

from os2models.base import OS2Base

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------


class Employee(OS2Base):
    type: Literal["employee"] = "employee"
    uuid: UUID
    name: str
    cpr_no: Optional[str] = None
    seniority: Optional[str] = None
