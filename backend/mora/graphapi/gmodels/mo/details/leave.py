# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic import Field

from .._shared import MOBase
from .._shared import Validity


class LeaveBase(MOBase):
    """A MO leave object."""

    type_: str = Field("leave", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the leave object.")


class LeaveRead(LeaveBase):
    """A MO leave read object."""

    employee_uuid: UUID = Field(
        description="UUID of the employee related to the leave."
    )
    leave_type_uuid: UUID = Field(description="UUID of the leave type klasse.")
    engagement_uuid: UUID = Field(
        description="UUID of the engagement related to the leave."
    )
