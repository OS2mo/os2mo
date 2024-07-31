# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from pydantic.v1 import Field
from pydantic.v1 import validator

from .._shared import MOBase
from .._shared import Validity


class ManagerRead(MOBase):
    """A MO ManagerRead object."""

    type_: str = Field("manager", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the manager object.")

    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the manager."
    )
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the manager."
    )
    manager_type_uuid: UUID | None = Field(description="UUID of the manager type.")
    manager_level_uuid: UUID | None = Field(description="UUID of the manager level.")
    responsibility_uuids: list[UUID] | None = Field(
        description="List of UUID's of the responsibilities."
    )

    @validator("employee_uuid", pre=True)
    def empty_string_is_none(cls, value: Any) -> Any:
        """Convert UUID-or-empty-string type back to a proper optional UUID type.

        MO models an empty employee by None (sane), but LoRa represents it by the empty
        string (insane)."""
        if value == "":
            return None
        return value
