#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from uuid import UUID

from pydantic import Field
from pydantic import validator

from .._shared import AssociationType
from .._shared import DynamicClasses
from .._shared import EmployeeRef
from .._shared import ITUserRef
from .._shared import JobFunction
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Primary
from .._shared import Validity
from ._shared import Details

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

    org_unit_uuid: UUID = Field(
        description="UUID of the organisation unit related to the association."
    )
    employee_uuid: UUID = Field(
        description="UUID of the employee related to the association."
    )
    association_type_uuid: Optional[UUID] = Field(
        description="UUID of the association type."
    )
    primary_uuid: Optional[UUID] = Field(
        description="UUID of the primary type of the association."
    )
    substitute_uuid: Optional[UUID] = Field(
        description="UUID of the substitute for the employee in the association."
    )
    job_function_uuid: Optional[UUID] = Field(
        description="UUID of a job function class, only defined for 'IT associations.'"
    )
    it_user_uuid: Optional[UUID] = Field(
        description="UUID of an 'ITUser' model, only defined for 'IT associations.'"
    )


class AssociationWrite(AssociationBase):
    """A MO AssociationWrite object."""

    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit for the association."
    )
    employee: EmployeeRef = Field(
        description=(
            "Reference to the employee for which the engagement should be created."
        )
    )
    association_type: AssociationType = Field(
        description="Reference to the association type klasse."
    )
    primary: Optional[Primary] = Field(
        description=(
            "Reference to the primary klasse for the created association object."
        )
    )
    substitute: Optional[EmployeeRef] = Field(
        description=(
            "Reference to the substitute for the employee in the association object."
        )
    )
    job_function: Optional[JobFunction] = Field(
        description=(
            "References a job function class (only defined for 'IT associations.')"
        )
    )
    it_user: Optional[ITUserRef] = Field(
        description="References an 'ITUser' (only defined for 'IT associations.')"
    )

    @validator("job_function", "it_user", always=True)
    def validate_mutually_exclusive(cls, v: UUID, values: Dict[str, UUID]) -> UUID:
        if values.get("substitute") and v:
            raise ValueError(
                "'substitute' must be None if 'job_function' or 'it_user' are not None"
            )
        return v


class AssociationDetail(AssociationWrite, Details):
    pass


class Association(MOBase):
    """
    A MO association object.
    """

    type_: Literal["association"] = Field(
        "association", alias="type", description="The object type."
    )
    org_unit: OrgUnitRef = Field(
        description=(
            "Reference to the organisation unit for which the association should be "
            "created."
        )
    )
    person: PersonRef = Field(
        description=(
            "Reference to the person for which the association should be created."
        )
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
        org_unit_uuid: UUID,
        person_uuid: UUID,
        association_type_uuid: UUID,
        from_date: str,
        to_date: Optional[str] = None,
        uuid: Optional[UUID] = None,
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