#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal
from typing import Optional

from pydantic import Field
from pydantic import validator

from ._shared import MOBase
from ramodels.base import tz_isodate

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------


class Employee(MOBase):
    """
    Attributes:
        type:
        name:
        cpr_no:
        seniority:
    """

    type: Literal["employee"] = "employee"
    name: str
    cpr_no: Optional[str] = Field(regex=r"^\d{9}[1-9]$")
    seniority: Optional[datetime]

    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None

    @validator("cpr_no")
    def validate_cpr(cls, cpr_no: Optional[str]) -> Optional[str]:
        if cpr_no is None:
            return None

        # The string is validated with regex first, so we know this works
        # We only obtain the most significant digit of the code part, since it's
        # what we need for century calculations,
        # cf. https://da.wikipedia.org/wiki/CPR-nummer
        day, month = (cpr_no[0:2], cpr_no[2:4])
        year, code_msd = map(int, (cpr_no[4:6], cpr_no[6]))

        # TODO: let's do pattern matching in 3.10:
        # https://www.python.org/dev/peps/pep-0622/ <3
        century: int = 0
        if code_msd < 4:
            century = 1900
        elif code_msd in {4, 9}:
            if 0 <= year <= 36:
                century = 2000
            else:
                century = 1900
        elif 5 <= code_msd <= 8:
            if 0 <= year <= 57:
                century = 2000
            else:
                century = 1800

        err_msg = f"CPR number {cpr_no} is not valid."
        # Removed because that never happens.
        # if century not in {1800, 1900, 2000}:
        #     raise ValueError(err_msg)
        try:
            date.fromisoformat(f"{century+year}-{month}-{day}")
        except Exception:
            raise ValueError(err_msg)

        return cpr_no
