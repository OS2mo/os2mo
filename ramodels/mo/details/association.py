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

from .._shared import AssociationType
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Validity

# --------------------------------------------------------------------------------------
# Engagement models
# --------------------------------------------------------------------------------------


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
