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

from .._shared import ITSystemRef
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Validity


# --------------------------------------------------------------------------------------
# IT Systems
# --------------------------------------------------------------------------------------


class ITSystemBindingBase(MOBase):
    """A MO IT system binding object."""

    type_: str = Field("it", alias="type", description="The object type.")
    validity: Validity = Field(description="Validity of the IT system binding object.")


class ITSystemBindingRead(ITSystemBindingBase):
    """A MO IT system binding read object."""

    itsystem: UUID = Field(description="UUID of the IT system of the binding.")
    person: Optional[UUID] = Field(
        description="Reference to the person related to the binding."
    )
    org_unit: Optional[UUID] = Field(
        description="Reference to the organisation unit related to the binding."
    )


class ITSystemBindingWrite(ITSystemBindingBase):
    """A MO IT system binding write object."""

    itsystem: ITSystemRef = Field(
        description="The IT system for which to create this binding."
    )
    person: Optional[PersonRef] = Field(
        description="Reference to the person object for which the binding should "
        "be created."
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description="Reference to the organisation unit for which the binding should "
        "be created."
    )


class ITSystemBinding(MOBase):
    type_: Literal["it"] = Field("it", alias="type", description="The object type.")
    user_key: str = Field(description="The IT system account name.")
    itsystem: ITSystemRef = Field(
        description="The IT system for which to create this binding."
    )
    person: Optional[PersonRef] = Field(
        description="Reference to the person object for which the binding should "
        "be created."
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description="Reference to the organisation unit for which the binding should "
        "be created."
    )
    validity: Validity = Field(
        description="Validity of the created IT system binding object."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        user_key: str,
        itsystem_uuid: UUID,
        from_date: str,
        uuid: Optional[UUID] = None,
        to_date: Optional[str] = None,
        person_uuid: Optional[UUID] = None,
        org_unit_uuid: Optional[UUID] = None,
    ) -> "ITSystemBinding":
        """
        Create an IT System Binding from simplified fields.
        """

        it_system = ITSystemRef(uuid=itsystem_uuid)
        person = PersonRef(uuid=person_uuid) if person_uuid else None
        org_unit = OrgUnitRef(uuid=org_unit_uuid) if org_unit_uuid else None
        validity = Validity(from_date=from_date, to_date=to_date)

        return cls(
            uuid=uuid,
            user_key=user_key,
            itsystem=it_system,
            person=person,
            org_unit=org_unit,
            validity=validity,
        )
