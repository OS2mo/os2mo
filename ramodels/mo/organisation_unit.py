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

from ._shared import MOBase
from ._shared import OrgUnitHierarchy
from ._shared import OrgUnitLevel
from ._shared import OrgUnitType
from ._shared import ParentRef
from ._shared import Validity

# --------------------------------------------------------------------------------------
# Organisation Unit model
# --------------------------------------------------------------------------------------


class OrganisationUnit(MOBase):
    type: Literal["org_unit"] = "org_unit"
    uuid: UUID
    user_key: str
    validity: Validity
    name: str
    parent: Optional[ParentRef] = None
    org_unit_hierarchy: Optional[OrgUnitHierarchy] = None
    org_unit_type: OrgUnitType
    org_unit_level: OrgUnitLevel

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        user_key: str,
        name: str,
        org_unit_type_uuid: UUID,
        org_unit_level_uuid: UUID,
        parent_uuid: Optional[UUID] = None,
        org_unit_hierarchy_uuid: Optional[UUID] = None,
        from_date: str = "1930-01-01",
        to_date: Optional[str] = None,
    ) -> "OrganisationUnit":
        parent = None
        if parent_uuid:
            parent = ParentRef(uuid=parent_uuid)

        org_unit_hierarchy = None
        if org_unit_hierarchy_uuid:
            org_unit_hierarchy = OrgUnitHierarchy(uuid=org_unit_hierarchy_uuid)

        return cls(
            uuid=uuid,
            user_key=user_key,
            validity=Validity(from_date=from_date, to_date=to_date),
            name=name,
            parent=parent,
            org_unit_hierarchy=org_unit_hierarchy,
            org_unit_type=OrgUnitType(uuid=org_unit_type_uuid),
            org_unit_level=OrgUnitLevel(uuid=org_unit_level_uuid),
        )
