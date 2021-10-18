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
from .details import EmployeeDetails
from ramodels.base import tz_isodate

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------

# Type aliases
DictStrAny = Dict[str, Any]


# Helper functions
def deprecation(message: str) -> None:
    """Raise a deprecation warning with `message` at stacklevel 2."""
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def split_name(name: str) -> Tuple[str, str]:
    """Split a name into first and last name.

    Args:
        name: The name to split.

    Returns:
        A 2-tuple containing first and last name.
    """
    split = name.split(" ", maxsplit=1)
    if len(split) == 1:
        split.append("")
    givenname, surname = split
    return givenname, surname


def validate_names(
    values: DictStrAny, name_key: str, givenname_key: str, surname_key: str
) -> DictStrAny:
    """Validate a name valies from a dictionary. Used in the Employee model validator.

    Args:
        values: Value dict to validate.
        name_key: The key for the name value.
        givenname_key: The key for the first name value.
        surname_key: The key for the last name value.

    Raises:
        ValueError: If both `name_key` and any of the `givenname_key`, `surname_key`
            are given, as they are mutually exclusive.

    Returns:
        The value dict, untouched.
    """
    if values.get(name_key) is not None:
        # Both name and given/surname are given erroneously
        if values.get(givenname_key) is not None or values.get(surname_key) is not None:
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
    """MO Employee data model."""

    type_: Literal["employee"] = Field(
        "employee", alias="type", description="The object type"
    )
    givenname: str = Field(None, description="Given name of the employee.")
    surname: str = Field(None, description="Surname of the employee.")
    name: Optional[str] = Field(
        description="The full name of the employee. "
        "This is deprecated, please use givenname/surname."
    )
    cpr_no: Optional[str] = Field(
        regex=r"^\d{10}$", description="CPR number of the employee."
    )
    seniority: Optional[datetime] = Field(description="Seniority of the employee.")
    user_key: Optional[str] = Field(description="Short, unique key.")
    org: Optional[OrganisationRef] = Field(
        description="Organisation reference. "
        "MO only supports one main organisation, so this is rarely used."
    )
    nickname_givenname: Optional[str] = Field(
        description="Given name part of nickname of the employee, if applicable."
    )
    nickname_surname: Optional[str] = Field(
        description="Surname part of nickname of the employee, if applicable."
    )
    nickname: Optional[str] = Field(
        description="Full nickname of the employee. "
        "Deprecated, please use given name/surname parts if needed."
    )
    details: Optional[List[EmployeeDetails]] = Field(
        description="Details to be created for the employee. "
        "Note that when this is used, the person reference is implicit in the payload."
    )

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
