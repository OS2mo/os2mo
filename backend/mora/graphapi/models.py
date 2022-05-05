#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from pydantic import BaseModel
from pydantic import Field

# --------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------


class HealthRead(BaseModel):
    """Payload model for health."""

    identifier: str = Field(description="Short, unique key.")


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

from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import EngagementAssociationType
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import EngagementType
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import LeaveRef
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import Validity

# --------------------------------------------------------------------------------------
# Engagement models
# --------------------------------------------------------------------------------------


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

from ramodels.mo._shared import EngagementAssociationType
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import Validity

# --------------------------------------------------------------------------------------
# Engagement models
# --------------------------------------------------------------------------------------
class EngagementAssociation(MOBase):
    """A MO engagement association object."""

    type_: str = Field(
        "engagement_association", alias="type", description="The object type."
    )
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
        to_date: Optional[str] = None,
        uuid: Optional[UUID] = None,
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
