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
    """
    Attributes:
        type:
        user_key:
        validity:
        name:
        parent:
        org_unit_hierarchy:
        org_unit_type:
        org_unit_level:
    """

    type: Literal["org_unit"] = "org_unit"
    user_key: str
    validity: Validity
    name: str
    parent: Optional[ParentRef]
    org_unit_hierarchy: Optional[OrgUnitHierarchy]
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
        from_date: str,
        parent_uuid: Optional[UUID] = None,
        org_unit_hierarchy_uuid: Optional[UUID] = None,
        to_date: Optional[str] = None,
    ) -> "OrganisationUnit":

        parent = ParentRef(uuid=parent_uuid) if parent_uuid else None
        org_unit_hierarchy = (
            OrgUnitHierarchy(uuid=org_unit_hierarchy_uuid)
            if org_unit_hierarchy_uuid
            else None
        )
        validity = Validity(from_date=from_date, to_date=to_date)

        return cls(
            uuid=uuid,
            user_key=user_key,
            validity=validity,
            name=name,
            parent=parent,
            org_unit_hierarchy=org_unit_hierarchy,
            org_unit_type=OrgUnitType(uuid=org_unit_type_uuid),
            org_unit_level=OrgUnitLevel(uuid=org_unit_level_uuid),
        )
