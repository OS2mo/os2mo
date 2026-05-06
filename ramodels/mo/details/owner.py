# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic import validator

from .._shared import MOBase
from .._shared import Validity


class OwnerBase(MOBase):
    """A MO owner object."""

    type_: str = Field("owner", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the owner object.")


class OwnerRead(OwnerBase):
    """A MO OwnerRead object."""

    owner_uuid: UUID | None = Field(description="UUID of the owner.")
    org_unit_uuid: UUID | None = Field(
        description="UUID of the organisation unit related to the owner."
    )
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the owner."
    )
    owner_inference_priority: str | None = Field(
        description="Inference priority, if set: `engagement_priority` or `association_priority`"
    )

    @validator("owner_uuid", pre=True)
    def empty_string_is_none(cls, value: Any) -> Any:
        """Convert UUID-or-empty-string type back to a proper optional UUID type.

        MO models an empty employee by None (sane), but LoRa represents it by the empty
        string (insane)."""
        if value == "":
            return None
        return value
