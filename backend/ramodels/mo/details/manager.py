# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from pydantic import Field

from .._shared import EmployeeRef
from .._shared import ManagerLevel
from .._shared import ManagerType
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Responsibility
from .._shared import Validity
from ._shared import Details


class ManagerBase(MOBase):
    """A MO manager object."""

    type_: str = Field("manager", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the manager object.")


class ManagerRead(ManagerBase):
    """A MO ManagerRead object."""

    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the manager."
    )
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the manager."
    )
    manager_type_uuid: UUID | None = Field(description="UUID of the manager type.")
    manager_level_uuid: UUID | None = Field(description="UUID of the manager level.")
    responsibility_uuids: list[UUID] | None = Field(
        description="List of UUID's of the responsibilities."
    )


class ManagerWrite(ManagerBase):
    """A MO ManagerWrite object."""

    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit for the manager."
    )
    employee: EmployeeRef | None = Field(
        description="Reference to the employee that will be the resulting manager."
    )
    manager_level: ManagerLevel | None = Field(
        description="Reference to the manager level klasse for the created manager."
    )
    manager_type: ManagerType | None = Field(
        description="Reference to the manager type klasse for the created manager."
    )
    responsibility: list[Responsibility] | None = Field(
        description="List of manager responsibility objects."
    )


class ManagerDetail(ManagerWrite, Details):
    pass


class Manager(MOBase):
    """A MO manager object."""

    type_: Literal["manager"] = Field(
        "manager", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description=(
            "Reference to the organisation unit "
            "for which the manager should be created."
        )
    )
    person: PersonRef = Field(
        description="Reference to the person that will be the resulting manager."
    )
    responsibility: list[Responsibility] = Field(
        description="Manager responsibility objects."
    )
    manager_level: ManagerLevel = Field(
        description="Reference to the manager level klasse for the created manager."
    )
    manager_type: ManagerType = Field(
        description="Reference to the manager type klasse for the created manager."
    )
    validity: Validity = Field(description="The validity of the created manager.")

    @classmethod
    def from_simplified_fields(
        cls,
        org_unit_uuid: UUID,
        person_uuid: UUID,
        responsibility_uuids: list[UUID],
        manager_level_uuid: UUID,
        manager_type_uuid: UUID,
        from_date: str,
        to_date: str | None = None,
        uuid: UUID | None = None,
    ) -> "Manager":
        """Create a manager from simplified fields."""
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
