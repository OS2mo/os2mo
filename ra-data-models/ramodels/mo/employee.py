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
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from ramodels.base import RABase
from ramodels.base import tz_isodate

from ._shared import MOBase
from ._shared import OpenValidity
from ._shared import OrganisationRef
from ._shared import validate_cpr
from ._shared import validate_names
from .details import EmployeeDetails

# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------

# Type aliases
DictStrAny = Dict[str, Any]


class EmployeeBase(MOBase):
    """A MO employee object."""

    type_: str = Field("employee", alias="type", description="The object type")
    cpr_no: Optional[str] = Field(
        regex=r"^\d{10}$", description="CPR number of the employee."
    )
    seniority: Optional[date] = Field(description="Seniority of the employee.")
    givenname: str = Field(description="Given name of the employee.")
    surname: str = Field(description="Surname of the employee.")
    nickname_givenname: Optional[str] = Field(
        description="Given name part of nickname of the employee."
    )
    nickname_surname: Optional[str] = Field(
        description="Surname part of nickname of the employee."
    )

    @validator("seniority", pre=True)
    def parse_datetime(cls, seniority: Any) -> Any:
        try:
            return datetime.fromisoformat(seniority).date()
        except (ValueError, TypeError):
            return seniority


class EmployeeRead(EmployeeBase):
    validity: OpenValidity = Field(description="Validity of the employee.")

    @root_validator(pre=True)
    def handle_deprecated_keys(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values.pop("name", None)
        values.pop("nickname", None)
        return values


class EmployeeWrite(EmployeeBase):
    name: Optional[str] = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    nickname: Optional[str] = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )
    details: Optional[List[EmployeeDetails]] = Field(
        description=(
            "Details to be created for the employee. Note that when this is used, the"
            " employee reference is implicit in the payload."
        )
    )

    @root_validator(pre=True)
    def validate_name(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(values, "name", "givenname", "surname")

    @root_validator(pre=True)
    def validate_nickname(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(
            values, "nickname", "nickname_givenname", "nickname_surname"
        )

    _validate_cpr = validator("cpr_no", allow_reuse=True)(validate_cpr)

    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None


class Employee(MOBase):
    """MO Employee data model."""

    type_: Literal["employee"] = Field(
        "employee", alias="type", description="The object type"
    )
    givenname: str = Field(None, description="Given name of the employee.")
    surname: str = Field(None, description="Surname of the employee.")
    name: Optional[str] = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    cpr_no: Optional[str] = Field(
        regex=r"^\d{10}$", description="CPR number of the employee."
    )
    seniority: Optional[datetime] = Field(description="Seniority of the employee.")
    org: Optional[OrganisationRef] = Field(
        description=(
            "Organisation reference. "
            "MO only supports one main organisation, so this is rarely used."
        )
    )
    nickname_givenname: Optional[str] = Field(
        description="Given name part of nickname of the employee, if applicable."
    )
    nickname_surname: Optional[str] = Field(
        description="Surname part of nickname of the employee, if applicable."
    )
    nickname: Optional[str] = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )
    details: Optional[List[EmployeeDetails]] = Field(
        description=(
            "Details to be created for the employee. Note that when this is used, the"
            " employee reference is implicit in the payload."
        )
    )

    @root_validator(pre=True)
    def validate_name(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(values, "name", "givenname", "surname")

    @root_validator(pre=True)
    def validate_nickname(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(
            values, "nickname", "nickname_givenname", "nickname_surname"
        )

    _validate_cpr = validator("cpr_no", allow_reuse=True)(validate_cpr)

    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None


class EmployeeCreateOrg(MOBase):
    """Representation of the organization which a org-unit belongs to.

    When creating an employee.
    """

    name: str = Field(description="Name of the organization.")


class EmployeeCreate(BaseModel):
    name: str = Field(description="Name of the new employee.")

    cpr_no: str = Field(
        description="CPR Number for the new employee.",
        regex=r"^\d{10}$",
    )

    org: EmployeeCreateOrg = Field(
        description="Main organisation the new employee belongs to."
    )

    details: List[dict] = Field(
        description="Details about the relations to create for the employee."
    )

    def to_dict(self) -> dict:
        """Converts pydantic class to an anonymous dict + converts fields."""
        return EmployeeCreate.convert_dict_fields(self.dict(by_alias=True))

    @staticmethod
    def convert_dict_fields(dict_to_convert: dict) -> dict:
        for key in dict_to_convert.keys():
            if isinstance(dict_to_convert[key], dict):
                dict_to_convert[key] = EmployeeCreate.convert_dict_fields(
                    dict_to_convert[key]
                )
                continue

            if isinstance(dict_to_convert[key], UUID):
                dict_to_convert[key] = str(dict_to_convert[key])
                continue

            if isinstance(dict_to_convert[key], datetime):
                dict_to_convert[key] = dict_to_convert[key].isoformat()
                continue

        return dict_to_convert


class EmployeeTerminate(RABase):
    validity: OpenValidity
    vacate: Optional[bool] = Field(
        description="Specifies if the termination was vacate related.. "
        "Leaders & Owners are not allowed to be removed, they are just vacated.",
        default=False,
    )
