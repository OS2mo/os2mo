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

from ._shared import OrgUnitRef
from ._shared import Person
from ._shared import Validity
from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# Manager implementations
# --------------------------------------------------------------------------------------


class Responsibility(RABase):
    uuid: UUID


class ManagerLevel(RABase):
    uuid: UUID


class ManagerType(RABase):
    uuid: UUID


# --------------------------------------------------------------------------------------
# Manager model
# --------------------------------------------------------------------------------------


class Manager(RABase):
    type: Literal["manager"] = "manager"
    uuid: UUID
    # user_key: str
    org_unit: OrgUnitRef
    person: Person
    responsibility: List[Responsibility]
    manager_level: ManagerLevel
    manager_type: ManagerType
    validity: Validity

    @classmethod
    def from_simplified_fields(
        cls,
        uuid: UUID,
        # user_key: str,
        org_unit_uuid: UUID,
        person_uuid: UUID,
        responsibility_uuid: UUID,
        manager_level_uuid: UUID,
        manager_type_uuid: UUID,
        from_date: str = "1930-01-01",
        to_date: Optional[str] = None,
    ):
        person = Person(uuid=person_uuid)
        org_unit = OrgUnitRef(uuid=org_unit_uuid)
        responsibility = [Responsibility(uuid=responsibility_uuid)]
        manager_level = ManagerLevel(uuid=manager_level_uuid)
        manager_type = ManagerType(uuid=manager_type_uuid)
        validity = Validity(from_date=from_date, to_date=to_date)

        return cls(
            uuid=uuid,
            # user_key=        # user_key,
            org_unit=org_unit,
            person=person,
            responsibility=responsibility,
            manager_level=manager_level,
            manager_type=manager_type,
            validity=validity,
        )
