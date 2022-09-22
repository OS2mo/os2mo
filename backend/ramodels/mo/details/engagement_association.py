# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from pydantic import Field

from .._shared import EngagementAssociationType
from .._shared import EngagementRef
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import Validity


class EngagementAssociationBase(MOBase):
    """A MO engagement association object."""

    type_: str = Field(
        "engagement_association", alias="type", description="The object type."
    )
    validity: Validity = Field(description="Validity of the association object.")


class EngagementAssociationRead(EngagementAssociationBase):
    """A MO engagement association read object."""

    org_unit_uuid: UUID = Field(
        description=(
            "Reference to the organisation unit "
            "for which the engagement association should be created."
        )
    )
    engagement_uuid: UUID = Field(
        description=(
            "Reference to the engagement "
            "for which the engagement association should be created."
        )
    )
    engagement_association_type_uuid: UUID = Field(
        description=(
            "Reference to the engagement association type klasse "
            "for the created engagement association object."
        )
    )


class EngagementAssociation(MOBase):
    """A MO engagement association object."""

    type_: Literal["engagement_association"] = Field(
        "engagement_association", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description=(
            "Reference to the organisation unit "
            "for which the engagement association should be created."
        )
    )
    engagement: EngagementRef = Field(
        description=(
            "Reference to the engagement "
            "for which the engagement association should be created."
        )
    )
    engagement_association_type: EngagementAssociationType = Field(
        description=(
            "Reference to the engagement association type klasse "
            "for the created engagement association object."
        )
    )
    validity: Validity = Field(
        description="Validity of the created engagement association."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        org_unit_uuid: UUID,
        engagement_uuid: UUID,
        engagement_association_type_uuid: UUID,
        from_date: str,
        to_date: str | None = None,
        uuid: UUID | None = None,
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
