# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from pydantic import Field

from .._shared import EngagementType
from .._shared import JobFunction
from .._shared import LeaveRef
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Primary
from .._shared import Validity
from ._shared import Details


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


class EngagementWrite(EngagementBase):
    """A MO engagement write object."""

    org_unit: OrgUnitRef = Field(
        description=(
            "Reference to the organisation unit "
            "for which the engagement should be created."
        )
    )
    person: PersonRef = Field(
        description=(
            "Reference to the employee for which the engagement should be created."
        )
    )
    engagement_type: EngagementType = Field(
        description=(
            "Reference to the engagement type klasse for the created engagement object."
        )
    )
    # NOTE: Job function is set to optional in the current MO write code,
    # but that's an error. If payloads without a job function are posted,
    # MO fails spectacularly when reading the resulting engagement objects.
    job_function: JobFunction = Field(
        description=(
            "Reference to the job function klasse for the created engagement object."
        )
    )
    leave: LeaveRef | None = Field(
        description="Reference to the leave for the created engagement."
    )
    primary: Primary | None = Field(
        description="Reference to the primary klasse for the created engagement object."
    )


class EngagementDetail(EngagementWrite, Details):
    pass


class Engagement(MOBase):
    """A MO engagement object."""

    type_: Literal["engagement"] = Field(
        "engagement", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description=(
            "Reference to the organisation unit "
            "for which the engagement should be created."
        )
    )
    person: PersonRef = Field(
        description=(
            "Reference to the person for which the engagement should be created."
        )
    )
    job_function: JobFunction = Field(
        description=(
            "Reference to the job function klasse for the created engagement object."
        )
    )
    engagement_type: EngagementType = Field(
        description=(
            "Reference to the engagement type klasse for the created engagement object."
        )
    )
    validity: Validity = Field(description="Validity of the created engagement object.")
    primary: Primary | None = Field(
        description="Reference to the primary klasse for the created engagement object."
    )
    user_key: str = Field(description="Short, unique key.")
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

    @classmethod
    def from_simplified_fields(
        cls,
        org_unit_uuid: UUID,
        person_uuid: UUID,
        job_function_uuid: UUID,
        engagement_type_uuid: UUID,
        user_key: str,
        from_date: str,
        to_date: str | None = None,
        uuid: UUID | None = None,
        primary_uuid: UUID | None = None,
        extension_1: str | None = None,
        extension_2: str | None = None,
        extension_3: str | None = None,
        extension_4: str | None = None,
        extension_5: str | None = None,
        extension_6: str | None = None,
        extension_7: str | None = None,
        extension_8: str | None = None,
        extension_9: str | None = None,
        extension_10: str | None = None,
    ) -> "Engagement":
        """Create an engagement from simplified fields."""
        org_unit = OrgUnitRef(uuid=org_unit_uuid)
        person = PersonRef(uuid=person_uuid)
        job_function = JobFunction(uuid=job_function_uuid)
        engagement_type = EngagementType(uuid=engagement_type_uuid)
        validity = Validity(from_date=from_date, to_date=to_date)
        primary = Primary(uuid=primary_uuid) if primary_uuid else None
        return cls(
            uuid=uuid,
            org_unit=org_unit,
            person=person,
            job_function=job_function,
            engagement_type=engagement_type,
            validity=validity,
            primary=primary,
            user_key=user_key,
            extension_1=extension_1,
            extension_2=extension_2,
            extension_3=extension_3,
            extension_4=extension_4,
            extension_5=extension_5,
            extension_6=extension_6,
            extension_7=extension_7,
            extension_8=extension_8,
            extension_9=extension_9,
            extension_10=extension_10,
        )
