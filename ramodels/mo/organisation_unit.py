#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import List
from typing import Literal
from typing import Optional
from uuid import UUID

from pydantic import Field

from ._shared import MOBase
from ._shared import OrgUnitHierarchy
from ._shared import OrgUnitLevel
from ._shared import OrgUnitType
from ._shared import ParentRef
from ._shared import Validity
from .details import OrgUnitDetails

# --------------------------------------------------------------------------------------
# Organisation Unit model
# --------------------------------------------------------------------------------------


class OrganisationUnit(MOBase):
    """A MO organisation unit object."""

    type_: Literal["org_unit"] = Field(
        "org_unit", alias="type", description="The object type."
    )
    user_key: str = Field(description="Short, unique key.")
    validity: Validity = Field(description="Validity of the created organisation unit.")
    name: str = Field(description="Name of the created organisation unit.")
    parent: Optional[ParentRef] = Field(
        description="Reference to the parent organisation unit, if applicable."
    )
    org_unit_hierarchy: Optional[OrgUnitHierarchy] = Field(
        description="Reference to the organisation unit hierarchy type, if applicable."
    )
    org_unit_type: OrgUnitType = Field(
        description="Reference to the organisation unit type."
    )
    org_unit_level: OrgUnitLevel = Field(
        description="Reference to the organisation unit level type."
    )
    details: Optional[List[OrgUnitDetails]] = Field(
        description="Details to be created for the organisation unit. "
        "Note that when this is used, the organisation unit reference "
        "is implicit in the payload."
    )

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
        """Create an organisation unit from simplified fields."""
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
