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

from .._shared import AddressType
from .._shared import EngagementRef
from .._shared import MOBase
from .._shared import OrganisationRef
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Validity
from .._shared import Visibility


# --------------------------------------------------------------------------------------
# Address model
# --------------------------------------------------------------------------------------


class Address(MOBase):
    """
    Attributes:
        type:
        value:
        value2:
        address_type:
        org:
        person:
        org_unit:
        engagement:
        validity:
        visibility:
    """

    type: Literal["address"] = "address"
    value: str
    value2: Optional[str]
    address_type: AddressType
    org: Optional[OrganisationRef]
    person: Optional[PersonRef]
    org_unit: Optional[OrgUnitRef]
    engagement: Optional[EngagementRef]
    validity: Validity
    visibility: Optional[Visibility]

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        value: str,
        address_type_uuid: UUID,
        from_date: str,
        to_date: Optional[str] = None,
        value2: Optional[str] = None,
        person_uuid: Optional[UUID] = None,
        org_unit_uuid: Optional[UUID] = None,
        engagement_uuid: Optional[UUID] = None,
        visibility_uuid: Optional[UUID] = None,
        org_uuid: Optional[UUID] = None,
    ) -> "Address":
        address_type = AddressType(uuid=address_type_uuid)
        org = OrganisationRef(uuid=org_uuid) if org_uuid else None
        validity = Validity(from_date=from_date, to_date=to_date)
        person = PersonRef(uuid=person_uuid) if person_uuid else None
        org_unit = OrgUnitRef(uuid=org_unit_uuid) if org_unit_uuid else None
        engagement = EngagementRef(uuid=engagement_uuid) if engagement_uuid else None
        visibility = Visibility(uuid=visibility_uuid) if visibility_uuid else None
        return cls(
            uuid=uuid,
            value=value,
            value2=value2,
            address_type=address_type,
            org=org,
            person=person,
            org_unit=org_unit,
            engagement=engagement,
            visibility=visibility,
            validity=validity,
        )
