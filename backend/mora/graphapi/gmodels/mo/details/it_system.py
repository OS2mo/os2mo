# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from .._shared import MOBase
from .._shared import OpenValidity
from .._shared import Validity


class ITSystemRead(MOBase):
    """Payload model for IT systems."""

    type_: str = Field("itsystem", alias="type", description="The object type")
    name: str = Field(description="Name/titel of the itsystem.")
    user_key: str = Field(description="Short, unique key.")
    system_type: str | None = Field(description="The ITSystem type.")
    validity: OpenValidity = Field(description="Validity of the IT system object.")


class ITUserRead(MOBase):
    """A MO IT user read object."""

    type_: str = Field("it", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the IT user object.")

    itsystem_uuid: UUID = Field(description="UUID of the ITSystem related to the user.")
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the user."
    )
    org_unit_uuid: UUID | None = Field(
        description="UUID organisation unit related to the user."
    )
    engagement_uuid: UUID | None = Field(
        description="UUID of the engagement related to the user."
    )
    engagement_uuids: list[UUID] | None = Field(
        description="Optional list of UUIDs of connected engagements"
    )
    primary_uuid: UUID | None = Field(
        description="UUID of an associated `primary_type` class."
    )
    external_id: str | None = Field(
        description="ID of the user account in the external system."
    )
