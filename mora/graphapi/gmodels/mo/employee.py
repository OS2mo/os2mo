# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ._shared import MOBase
from ._shared import OpenValidity

# Type aliases
DictStrAny = dict[str, Any]


class EmployeeRead(MOBase):
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

    validity: OpenValidity = Field(description="Validity of the employee.")

    @root_validator(pre=True)
    def handle_deprecated_keys(cls, values: dict[str, Any]) -> dict[str, Any]:
        values.pop("name", None)
        values.pop("nickname", None)
        return values
