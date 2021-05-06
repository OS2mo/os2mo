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

from ._shared import AddressType
from ._shared import EngagementRef
from ._shared import MOBase
from ._shared import OrganisationRef
from ._shared import OrgUnitRef
from ._shared import PersonRef
from ._shared import Validity
from ._shared import Visibility


# --------------------------------------------------------------------------------------
# Address model
# --------------------------------------------------------------------------------------


class Address(MOBase):
    type: Literal["address"] = "address"
    value: str
    value2: Optional[str]
    address_type: AddressType
    org: OrganisationRef
    person: Optional[PersonRef] = None
    org_unit: Optional[OrgUnitRef] = None
    engagement: Optional[EngagementRef] = None
    validity: Validity
    visibility: Optional[Visibility] = None

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        value: str,
        value2: Optional[str],
        address_type_uuid: UUID,
        org_uuid: UUID,
        from_date: str,
        to_date: Optional[str] = None,
        person_uuid: Optional[UUID] = None,
        org_unit_uuid: Optional[UUID] = None,
        engagement_uuid: Optional[UUID] = None,
        visibility_uuid: Optional[UUID] = None,
    ):
        address_type = AddressType(uuid=address_type_uuid)
        org = OrganisationRef(uuid=org_uuid)
        validity = Validity(from_date=from_date, to_date=to_date)
        person = None
        if person_uuid:
            person = PersonRef(uuid=person_uuid)
        org_unit = None
        if org_unit_uuid:
            org_unit = OrgUnitRef(uuid=org_unit_uuid)
        engagement = None
        if engagement_uuid:
            engagement = EngagementRef(uuid=engagement_uuid)
        visibility = None
        if visibility_uuid:
            visibility = Visibility(uuid=visibility_uuid)
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
