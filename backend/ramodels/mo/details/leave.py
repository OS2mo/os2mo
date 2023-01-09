# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from pydantic import Field

from .._shared import EmployeeRef
from .._shared import EngagementRef
from .._shared import LeaveType
from .._shared import MOBase
from .._shared import PersonRef
from .._shared import Validity
from ._shared import Details


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
    engagement_uuid: UUID | None = Field(
        description="UUID of the engagement related to the leave."
    )


class LeaveWrite(LeaveBase):
    """A MO leave write object."""

    leave_type: LeaveType = Field(description="Reference to the leave type klasse.")
    employee: EmployeeRef = Field(
        description="Reference to the employee for which the leave should be created."
    )
    engagement: EngagementRef | None = Field(
        description="Reference to the engagement for which the leave should be created."
    )


class LeaveDetail(LeaveWrite, Details):
    pass


class Leave(MOBase):
    type_: Literal["leave"] = Field(
        "leave", alias="type", description="The object type."
    )
    leave_type: LeaveType = Field(description="Reference to the leave type facet")
    person: PersonRef = Field(
        description=(
            "Reference to the person object for which the role should be created."
        )
    )
    engagement: EngagementRef | None = Field(
        description="Reference to the engagement for which the role should be created."
    )
    validity: Validity = Field(description="Validity of the created role object.")
