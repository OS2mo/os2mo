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

from .._shared import AssociationType
from .._shared import DynamicClasses
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Primary
from .._shared import Validity

# --------------------------------------------------------------------------------------
# Engagement models
# --------------------------------------------------------------------------------------


class AssociationBase(MOBase):
    """A MO association object."""

    type_: str = Field("association", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the association object.")
    dynamic_classes: Optional[List[DynamicClasses]] = Field(
        description="Attached classes"
    )


class AssociationRead(AssociationBase):
    """A MO AssociationRead object."""

    org_unit: UUID = Field(
        description="UUID of the organisation unit related to the association."
    )
    person: UUID = Field(description="UUID of the person related to the association.")
    association_type: UUID = Field(description="UUID of the association type.")
    primary: Optional[UUID] = Field(
        description="UUID of the primary type of the association."
    )
    substitute: Optional[UUID] = Field(
        description="UUID of the substitute for the person in the association."
    )


class AssociationWrite(AssociationBase):
    """A MO AssociationWrite object."""

    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit for the association."
    )
    person: PersonRef = Field(
        description="Reference to the person for which the engagement should be "
        "created."
    )
    association_type: AssociationType = Field(
        description="Reference to the association type klasse."
    )
    primary: Optional[Primary] = Field(
        description="Reference to the primary klasse for the created association "
        "object."
    )
    substitute: Optional[PersonRef] = Field(
        description="Reference to the substitute for the person in the association "
        "object."
    )


class Association(MOBase):
    """
    A MO association object.
    """

    type_: Literal["association"] = Field(
        "association", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit "
        "for which the association should be created."
    )
    person: PersonRef = Field(
        description="Reference to the person "
        "for which the association should be created."
    )
    association_type: AssociationType = Field(
        description="Reference to the association type facet."
    )
    validity: Validity = Field(
        description="Validity of the created association object."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        org_unit_uuid: UUID,
        person_uuid: UUID,
        association_type_uuid: UUID,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> "Association":
        """Create a new association from simplified fields."""
        validity = Validity(from_date=from_date, to_date=to_date)
        org_unit = OrgUnitRef(uuid=org_unit_uuid)
        person = PersonRef(uuid=person_uuid)
        association_type = AssociationType(uuid=association_type_uuid)
        return cls(
            uuid=uuid,
            org_unit=org_unit,
            person=person,
            association_type=association_type,
            validity=validity,
        )
