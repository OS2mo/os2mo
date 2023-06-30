# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from .._shared import MOBase
from .._shared import Validity


class OwnerBase(MOBase):
    """A MO owner object."""

    type_: str = Field("owner", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the owner object.")


class OwnerRead(OwnerBase):
    """A MO OwnerRead object."""

    org_unit_uuid: UUID | None = Field(
        description="UUID of the organisation unit related to the owner."
    )
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the owner."
    )
