#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Literal
from typing import Optional
from uuid import UUID

from pydantic import Field

from .._shared import EngagementAssociationType
from .._shared import EngagementRef
from .._shared import EngagementType
from .._shared import JobFunction
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Primary
from .._shared import Validity

# --------------------------------------------------------------------------------------
# Engagement models
# --------------------------------------------------------------------------------------


class EngagementBase(MOBase):
    """A MO engagement object."""

    type_: str = Field("engagement", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the engagement object.")
    fraction: Optional[int] = Field(
        description="Indication of contribution to the "
        "collection of engagements for the given employee."
    )
    extension_1: Optional[str] = Field(description="Optional extra information.")
    extension_2: Optional[str] = Field(description="Optional extra information.")
    extension_3: Optional[str] = Field(description="Optional extra information.")
    extension_4: Optional[str] = Field(description="Optional extra information.")
    extension_5: Optional[str] = Field(description="Optional extra information.")
    extension_6: Optional[str] = Field(description="Optional extra information.")
    extension_7: Optional[str] = Field(description="Optional extra information.")
    extension_8: Optional[str] = Field(description="Optional extra information.")
    extension_9: Optional[str] = Field(description="Optional extra information.")
    extension_10: Optional[str] = Field(description="Optional extra information.")


class EngagementRead(EngagementBase):
    """A MO engagement read object."""

    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the engagement."
    )
    person_uuid: UUID = Field(
        description="UUID of the person related to the engagement."
    )
    engagement_type_uuid: UUID = Field(
        description="UUID of the engagement type klasse of the engagement."
    )
    job_function_uuid: UUID = Field(
        description="UUID of the job function klasse of the engagement."
    )
    primary_uuid: Optional[UUID] = Field(
        description="UUID of the primary klasse of the engagement."
    )
    is_primary: Optional[bool] = Field(
        description="Indication of whether this engagement is the primary."
    )


class EngagementWrite(EngagementBase):
    """A MO engagement write object."""

    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit "
        "for which the engagement should be created."
    )
    person: PersonRef = Field(
        description="Reference to the person "
        "for which the engagement should be created."
    )
    engagement_type: EngagementType = Field(
        description="Reference to the engagement type klasse "
        "for the created engagement object."
    )
    # NOTE: Job function is set to optional in the current MO write code,
    # but that's an error. If payloads without a job function are posted,
    # MO fails spectacularly when reading the resulting engagement objects.
    job_function: JobFunction = Field(
        description="Reference to the job function klasse "
        "for the created engagement object."
    )
    primary: Optional[Primary] = Field(
        description="Reference to the primary klasse for the created engagement object."
    )


class Engagement(MOBase):
    """A MO engagement object."""

    type_: Literal["engagement"] = Field(
        "engagement", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit "
        "for which the engagement should be created."
    )
    person: PersonRef = Field(
        description="Reference to the person "
        "for which the engagement should be created."
    )
    job_function: JobFunction = Field(
        description="Reference to the job function klasse "
        "for the created engagement object."
    )
    engagement_type: EngagementType = Field(
        description="Reference to the engagement type klasse "
        "for the created engagement object."
    )
    validity: Validity = Field(description="Validity of the created engagement object.")
    primary: Primary = Field(
        description="Reference to the primary klasse for the created engagement object."
    )
    user_key: str = Field(description="Short, unique key.")
    extension_1: Optional[str] = Field(description="Optional extra information.")
    extension_2: Optional[str] = Field(description="Optional extra information.")
    extension_3: Optional[str] = Field(description="Optional extra information.")
    extension_4: Optional[str] = Field(description="Optional extra information.")
    extension_5: Optional[str] = Field(description="Optional extra information.")
    extension_6: Optional[str] = Field(description="Optional extra information.")
    extension_7: Optional[str] = Field(description="Optional extra information.")
    extension_8: Optional[str] = Field(description="Optional extra information.")
    extension_9: Optional[str] = Field(description="Optional extra information.")
    extension_10: Optional[str] = Field(description="Optional extra information.")

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        org_unit_uuid: UUID,
        person_uuid: UUID,
        job_function_uuid: UUID,
        engagement_type_uuid: UUID,
        primary_uuid: UUID,
        user_key: str,
        from_date: str,
        to_date: Optional[str] = None,
        extension_1: Optional[str] = None,
        extension_2: Optional[str] = None,
        extension_3: Optional[str] = None,
        extension_4: Optional[str] = None,
        extension_5: Optional[str] = None,
        extension_6: Optional[str] = None,
        extension_7: Optional[str] = None,
        extension_8: Optional[str] = None,
        extension_9: Optional[str] = None,
        extension_10: Optional[str] = None,
    ) -> "Engagement":
        """Create an engagement from simplified fields."""
        org_unit = OrgUnitRef(uuid=org_unit_uuid)
        person = PersonRef(uuid=person_uuid)
        job_function = JobFunction(uuid=job_function_uuid)
        engagement_type = EngagementType(uuid=engagement_type_uuid)
        validity = Validity(from_date=from_date, to_date=to_date)
        primary = Primary(uuid=primary_uuid)
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


class EngagementAssociation(MOBase):
    """A MO engagement association object."""

    type_: Literal["engagement_association"] = Field(
        "engagement_association", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit "
        "for which the engagement association should be created."
    )
    engagement: EngagementRef = Field(
        description="Reference to the engagement "
        "for which the engagement association should be created."
    )
    engagement_association_type: EngagementAssociationType = Field(
        description="Reference to the engagement association type klasse "
        "for the created engagement association object."
    )
    validity: Validity = Field(
        description="Validity of the created engagement association."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        org_unit_uuid: UUID,
        engagement_uuid: UUID,
        engagement_association_type_uuid: UUID,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> "EngagementAssociation":
        """Create an engagement association from simplified fields."""
        validity = Validity(from_date=from_date, to_date=to_date)
        org_unit = OrgUnitRef(uuid=org_unit_uuid)
        engagement = EngagementRef(uuid=engagement_uuid)
        engagement_association_type = EngagementAssociationType(
            uuid=engagement_association_type_uuid
        )
        return cls(
            uuid=uuid,
            org_unit=org_unit,
            engagement=engagement,
            engagement_association_type=engagement_association_type,
            validity=validity,
        )
