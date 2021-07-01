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


class Engagement(MOBase):
    """
    Attributes:
        type:
        org_unit:
        person:
        job_function:
        engagement_type:
        validity:
        primary:
        user_key:
        extension_1:
        extension_2:
        extension_3:
        extension_4:
        extension_5:
        extension_6:
        extension_7:
        extension_8:
        extension_9:
        extension_10:
    """

    type: Literal["engagement"] = "engagement"
    org_unit: OrgUnitRef
    person: PersonRef
    job_function: JobFunction
    engagement_type: EngagementType
    validity: Validity
    primary: Primary
    user_key: str
    extension_1: Optional[str]
    extension_2: Optional[str]
    extension_3: Optional[str]
    extension_4: Optional[str]
    extension_5: Optional[str]
    extension_6: Optional[str]
    extension_7: Optional[str]
    extension_8: Optional[str]
    extension_9: Optional[str]
    extension_10: Optional[str]

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
    type: Literal["engagement_association"] = "engagement_association"
    org_unit: OrgUnitRef
    engagement: EngagementRef
    engagement_association_type: EngagementAssociationType
    validity: Validity

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
