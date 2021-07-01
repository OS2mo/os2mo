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

from .._shared import ManagerLevel
from .._shared import ManagerType
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Responsibility
from .._shared import Validity

# --------------------------------------------------------------------------------------
# Manager implementations
# --------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------
# Manager model
# --------------------------------------------------------------------------------------


class Manager(MOBase):
    """
    Attributes:
        type:
        org_unit:
        person:
        responsibility:
        manager_level:
        manager_type:
        validity:
    """

    type: Literal["manager"] = "manager"
    org_unit: OrgUnitRef
    person: PersonRef
    responsibility: List[Responsibility]
    manager_level: ManagerLevel
    manager_type: ManagerType
    validity: Validity

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        org_unit_uuid: UUID,
        person_uuid: UUID,
        responsibility_uuids: List[UUID],
        manager_level_uuid: UUID,
        manager_type_uuid: UUID,
        from_date: str,
        to_date: Optional[str] = None,
    ) -> "Manager":
        person = PersonRef(uuid=person_uuid)
        org_unit = OrgUnitRef(uuid=org_unit_uuid)
        responsibility = [
            Responsibility(uuid=r_uuid) for r_uuid in responsibility_uuids
        ]
        manager_level = ManagerLevel(uuid=manager_level_uuid)
        manager_type = ManagerType(uuid=manager_type_uuid)
        validity = Validity(from_date=from_date, to_date=to_date)

        return cls(
            uuid=uuid,
            org_unit=org_unit,
            person=person,
            responsibility=responsibility,
            manager_level=manager_level,
            manager_type=manager_type,
            validity=validity,
        )
