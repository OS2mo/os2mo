# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ._shared import MOBase
from ._shared import OpenValidity
from ._shared import OrganisationRef
from ._shared import validate_cpr
from ._shared import validate_names
from .details import EmployeeDetails
from ramodels.base import RABase
from ramodels.base import tz_isodate


# Type aliases
DictStrAny = dict[str, Any]


class EmployeeBase(MOBase):
    """A MO employee object."""

    type_: str = Field("employee", alias="type", description="The object type")
    cpr_no: str | None = Field(
        regex=r"^\d{10}$", description="CPR number of the employee."
    )
    seniority: date | None = Field(description="Seniority of the employee.")
    givenname: str = Field(description="Given name of the employee.")
    surname: str = Field(description="Surname of the employee.")
    nickname_givenname: str | None = Field(
        description="Given name part of nickname of the employee."
    )
    nickname_surname: str | None = Field(
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
    def handle_deprecated_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        values.pop("name", None)
        values.pop("nickname", None)
        return values


class EmployeeWrite(EmployeeBase):
    name: str | None = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    nickname: str | None = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )
    details: list[EmployeeDetails] | None = Field(
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
    def parse_seniority(cls, seniority: Any | None) -> datetime | None:
        return tz_isodate(seniority) if seniority is not None else None


class Employee(MOBase):
    """MO Employee data model."""

    type_: Literal["employee"] = Field(
        "employee", alias="type", description="The object type"
    )
    givenname: str = Field(None, description="Given name of the employee.")
    surname: str = Field(None, description="Surname of the employee.")
    name: str | None = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    cpr_no: str | None = Field(
        regex=r"^\d{10}$", description="CPR number of the employee."
    )
    seniority: datetime | None = Field(description="Seniority of the employee.")
    org: OrganisationRef | None = Field(
        description=(
            "Organisation reference. "
            "MO only supports one main organisation, so this is rarely used."
        )
    )
    nickname_givenname: str | None = Field(
        description="Given name part of nickname of the employee, if applicable."
    )
    nickname_surname: str | None = Field(
        description="Surname part of nickname of the employee, if applicable."
    )
    nickname: str | None = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )
    details: list[EmployeeDetails] | None = Field(
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
    def parse_seniority(cls, seniority: Any | None) -> datetime | None:
        return tz_isodate(seniority) if seniority is not None else None


class EmployeeTerminate(RABase):
    validity: OpenValidity
    vacate: bool | None = Field(
        description="Specifies if the termination was vacate related.. "
        "Leaders & Owners are not allowed to be removed, they are just vacated.",
        default=False,
    )
