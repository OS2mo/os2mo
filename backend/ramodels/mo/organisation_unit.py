# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from pydantic import Field

from ..base import RABase
from ._shared import MOBase
from ._shared import OpenValidity
from ._shared import OrgUnitHierarchy
from ._shared import OrgUnitLevel
from ._shared import OrgUnitType
from ._shared import ParentRef
from ._shared import TimePlanning
from ._shared import Validity
from .details import OrgUnitDetails


class OrganisationUnitBase(MOBase):
    """A MO organisation unit object."""

    type_: str = Field("org_unit", alias="type", description="The object type.")
    name: str = Field(description="Name of the created organisation unit.")
    validity: Validity = Field(description="Validity of the created organisation unit.")


class OrganisationUnitRead(OrganisationUnitBase):
    parent_uuid: UUID | None = Field(
        description="UUID of the parent organisation unit."
    )
    org_unit_hierarchy: UUID | None = Field(
        description="UUID of the organisation unit hierarchy."
    )
    unit_type_uuid: UUID | None = Field(
        description="UUID of the organisation unit type."
    )
    org_unit_level_uuid: UUID | None = Field(
        description="UUID of the organisation unit level."
    )
    time_planning_uuid: UUID | None = Field(
        description="UUID of the time planning object."
    )


class OrganisationUnitWrite(OrganisationUnitBase):
    parent: ParentRef | None = Field(
        description="Reference to the parent organisation unit."
    )
    org_unit_hierarchy: OrgUnitHierarchy | None = Field(
        description="Reference to the organisation unit hierarchy type."
    )
    org_unit_type: OrgUnitType | None = Field(
        description="Reference to the organisation unit type."
    )
    org_unit_level: OrgUnitLevel | None = Field(
        description="Reference to the organisation unit level type."
    )
    time_planning: TimePlanning | None = Field(
        description="Reference to the time planning type."
    )
    details: list[OrgUnitDetails] | None = Field(
        description=(
            "Details to be created for the organisation unit. "
            "Note that when this is used, the organisation unit reference "
            "is implicit in the payload."
        )
    )


class OrganisationUnit(MOBase):
    """A MO organisation unit object."""

    type_: Literal["org_unit"] = Field(
        "org_unit", alias="type", description="The object type."
    )
    user_key: str = Field(description="Short, unique key.")
    validity: Validity = Field(description="Validity of the created organisation unit.")
    name: str = Field(description="Name of the created organisation unit.")
    parent: ParentRef | None = Field(
        description="Reference to the parent organisation unit, if applicable."
    )
    org_unit_hierarchy: OrgUnitHierarchy | None = Field(
        description="Reference to the organisation unit hierarchy type, if applicable."
    )
    org_unit_type: OrgUnitType = Field(
        description="Reference to the organisation unit type."
    )
    org_unit_level: OrgUnitLevel | None = Field(
        description="Reference to the organisation unit level type."
    )
    details: list[OrgUnitDetails] | None = Field(
        description=(
            "Details to be created for the organisation unit. "
            "Note that when this is used, the organisation unit reference "
            "is implicit in the payload."
        )
    )

    @classmethod
    def from_simplified_fields(
        cls,
        user_key: str,
        name: str,
        org_unit_type_uuid: UUID,
        from_date: str,
        uuid: UUID | None = None,
        parent_uuid: UUID | None = None,
        org_unit_level_uuid: UUID | None = None,
        org_unit_hierarchy_uuid: UUID | None = None,
        to_date: str | None = None,
    ) -> "OrganisationUnit":
        """Create an organisation unit from simplified fields."""
        parent = ParentRef(uuid=parent_uuid) if parent_uuid else None
        org_unit_hierarchy = (
            OrgUnitHierarchy(uuid=org_unit_hierarchy_uuid)
            if org_unit_hierarchy_uuid
            else None
        )
        org_unit_level = (
            OrgUnitLevel(uuid=org_unit_level_uuid) if org_unit_level_uuid else None
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
            org_unit_level=org_unit_level,
        )


class OrganisationUnitTerminate(RABase):
    validity: OpenValidity
