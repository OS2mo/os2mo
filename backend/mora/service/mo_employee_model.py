#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from pydantic.config import Extra
from pydantic.main import BaseModel

from .. import config
from ramodels.base import tz_isodate
from ramodels.mo._shared import validate_cpr
from ramodels.mo._shared import validate_names

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------

# Type aliases
DictStrAny = Dict[str, Any]


class Org(BaseModel):
    name: Optional[str] = Field(description="Name of the organisation")
    user_key: Optional[str] = Field(
        description="Optional notes about org or department"
    )
    uuid: UUID = Field(description="Uuid of the org (Generated when org created)")


class MOEmployeeWrite(BaseModel):
    """
    Pydantic model for creation and updating of employees.
    """

    cpr_no: Optional[str] = Field(description="CPR number of the employee.")

    org: Org = Field(description="Org unit the employee belongs to")
    user_key: Optional[str] = Field(
        description="Optional notes to eg. employee org or department"
    )
    uuid: Optional[UUID] = Field(
        description="Uuid of the employee (Generated when employee created)"
    )
    name: Optional[str] = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    givenname: Optional[str] = Field(description="Given name of the employee.")
    surname: Optional[str] = Field(description="Surname of the employee.")
    nickname: Optional[str] = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )

    nickname_givenname: Optional[str] = Field(
        description="Given name part of nickname of the employee, if applicable."
    )

    nickname_surname: Optional[str] = Field(
        description="Surname part of nickname of the employee, if applicable."
    )
    seniority: Optional[date] = Field(description="Seniority of the employee.")
    details: Optional[List] = Field(
        description=(
            "Details to be created for the employee. Note that when this is used, the"
            " employee reference is implicit in the payload."
        )
    )

    # Validating name vs givenname/surname as they are mutually exclusive
    @root_validator(pre=True)
    def validate_name(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(values, "name", "givenname", "surname")

    # Validating nickname vs nick_givenname/nick_surname as they are mutually exclusive
    @root_validator(pre=True)
    def validate_nickname(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(
            values, "nickname", "nickname_givenname", "nickname_surname"
        )

    # Validating cpr has correct syntax, in date-format.
    # Also checks if cpr should be validated as per flag
    # ("cpr_validate_birthdate") set in config.
    @validator("cpr_no", pre=True)
    def validate_cpr_no(cls, cpr: str) -> DictStrAny:
        if not config.get_settings().cpr_validate_birthdate:
            print(f"----------------WE DON'T WANT TO CHECK CPR - {cpr}")
            return cpr
        return validate_cpr(cpr)

    # Attempts to parse an incoming value as a timezone aware datetime
    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None

    class Config:
        extra = Extra.forbid
