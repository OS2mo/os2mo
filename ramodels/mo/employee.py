#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import warnings
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ._shared import MOBase
from ._shared import OrganisationRef
from .details import Details
from ramodels.base import tz_isodate

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------

# Type aliases
DictStrAny = Dict[str, Any]


# Helper functions
def deprecation(message: str) -> None:
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def split_name(name: str) -> Tuple[str, str]:
    split = name.split(" ", maxsplit=1)
    if len(split) == 1:
        split.append("")
    givenname, surname = split
    return givenname, surname


def validate_names(
    values: DictStrAny, name_key: str, givenname_key: str, surname_key: str
) -> Dict:
    if name_key in values:
        # Both name and given/surname are given erroneously
        if any([givenname_key in values, surname_key in values]):
            raise ValueError(
                f"{name_key} and {givenname_key}/{surname_key} are mutually exclusive"
            )
        # If only name is given, raise a deprecation warning and generate given/surname
        else:
            deprecation(
                f"{name_key} will be deprecated in a future version. "
                f"Prefer {givenname_key}/{surname_key} where possible"
            )
            values[givenname_key], values[surname_key] = split_name(values[name_key])

    return values


class Employee(MOBase):
    """MO Employee data model.

    Attributes:
        type_: Object type.
        givenname: Given name of the employee
        surname: Surname of the employee
        name: Full name of the employee - will be deprecated, use given name/surname
        cpr_no: CPR number of the employee
        seniority: Seniority of the employee
        user_key: Short, unique key identifying the employee
        org: The organisation with which the employee is associated
        nickname_givenname: Given name part of the employee's nickname
        nickname_surname: Surname part of the employee's nickname
        nickname: Full nickname of the employee - will be deprecated,
            use given name/surname
        details:  A list of details to be created for the employee.
    """

    type_: Literal["employee"] = Field("employee", alias="type")
    givenname: str = Field(None)
    surname: str = Field(None)
    name: Optional[str]
    cpr_no: Optional[str] = Field(regex=r"^\d{9}[1-9]$")
    seniority: Optional[datetime]
    user_key: Optional[str]
    org: Optional[OrganisationRef]
    nickname_givenname: Optional[str]
    nickname_surname: Optional[str]
    nickname: Optional[str]
    details: Optional[List[Details]]

    @root_validator(pre=True)
    def validate_name(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(values, "name", "givenname", "surname")

    @root_validator(pre=True)
    def validate_nickname(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(
            values, "nickname", "nickname_givenname", "nickname_surname"
        )

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

        try:
            date.fromisoformat(f"{century+year}-{month}-{day}")
        except Exception:
            raise ValueError("CPR number is invalid.")
        return cpr_no

    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None
