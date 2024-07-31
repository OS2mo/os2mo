# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from .._shared import MOBase
from .._shared import Validity


class EngagementBase(MOBase):
    """A MO engagement object."""

    type_: str = Field("engagement", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the engagement object.")
    fraction: int | None = Field(
        description=(
            "Indication of contribution to the "
            "collection of engagements for the given employee."
        )
    )
    extension_1: str | None = Field(description="Optional extra information.")
    extension_2: str | None = Field(description="Optional extra information.")
    extension_3: str | None = Field(description="Optional extra information.")
    extension_4: str | None = Field(description="Optional extra information.")
    extension_5: str | None = Field(description="Optional extra information.")
    extension_6: str | None = Field(description="Optional extra information.")
    extension_7: str | None = Field(description="Optional extra information.")
    extension_8: str | None = Field(description="Optional extra information.")
    extension_9: str | None = Field(description="Optional extra information.")
    extension_10: str | None = Field(description="Optional extra information.")


class EngagementRead(EngagementBase):
    """A MO engagement read object."""

    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the engagement."
    )
    employee_uuid: UUID = Field(
        description="UUID of the employee related to the engagement."
    )
    engagement_type_uuid: UUID = Field(
        description="UUID of the engagement type klasse of the engagement."
    )
    job_function_uuid: UUID = Field(
        description="UUID of the job function klasse of the engagement."
    )
    leave_uuid: UUID | None = Field(
        description="UUID of the leave related to the engagement."
    )
    primary_uuid: UUID | None = Field(
        description="UUID of the primary klasse of the engagement."
    )
