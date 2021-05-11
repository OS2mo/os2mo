#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime
from typing import Literal
from typing import Optional

from ._shared import MOBase

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------


class Employee(MOBase):
    type: Literal["employee"] = "employee"
    name: str
    cpr_no: Optional[str] = None
    seniority: Optional[datetime] = None
