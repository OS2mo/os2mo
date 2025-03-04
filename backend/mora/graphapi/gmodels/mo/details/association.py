# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic import validator

from .._shared import MOBase
from .._shared import Validity


class AssociationRead(MOBase):
    """A MO AssociationRead object."""

    type_: str = Field("association", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the association object.")
    dynamic_class_uuid: UUID | None = Field(description="Attached class")

    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the association."
    )
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the association."
    )
    association_type_uuid: UUID | None = Field(
        description="UUID of the association type."
    )
    primary_uuid: UUID | None = Field(
        description="UUID of the primary type of the association."
    )
    substitute_uuid: UUID | None = Field(
        description="UUID of the substitute for the employee in the association."
    )
    job_function_uuid: UUID | None = Field(
        description="UUID of a job function class, only defined for 'IT associations.'"
    )
    it_user_uuid: UUID | None = Field(
        description="UUID of an 'ITUser' model, only defined for 'IT associations.'"
    )

    @validator("employee_uuid", pre=True)
    def empty_string_is_none(cls, value: Any) -> Any:
        """Convert UUID-or-empty-string type back to a proper optional UUID type.

        MO models an empty employee by None (sane), but LoRa represents it by the empty
        string (insane)."""
        if value == "":  # pragma: no cover
            return None
        return value
