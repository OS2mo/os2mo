# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

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
    engagement_uuid: UUID | None = Field(
        description="UUID of the engagement that provides this manager-role."
    )
    manager_type_uuid: UUID | None = Field(description="UUID of the manager type.")
    manager_level_uuid: UUID | None = Field(description="UUID of the manager level.")
    responsibility_uuids: list[UUID] | None = Field(
        description="List of UUID's of the responsibilities."
    )
