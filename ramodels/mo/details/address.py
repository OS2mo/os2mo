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

from more_itertools import one
from pydantic import Field
from pydantic import root_validator

from .._shared import AddressType
from .._shared import DictStrAny
from .._shared import EmployeeRef
from .._shared import EngagementRef
from .._shared import MOBase
from .._shared import OrganisationRef
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Validity
from .._shared import Visibility
from ._shared import Details


# --------------------------------------------------------------------------------------
# Address model
# --------------------------------------------------------------------------------------


class AddressBase(MOBase):
    """
    A MO address object.
    """

    type_: str = Field("address", alias="type", description="The object type.")
    value: str = Field(description="Value of the address, e.g. street or phone number.")
    value2: Optional[str] = Field(description="Optional second value of the address.")
    validity: Validity = Field(description="Validity of the address object.")


class AddressRead(AddressBase):
    """
    A MO address read object.
    Note that one and only one of {employee, org_unit, engagement} are given at any
    time.
    """

    address_type_uuid: UUID = Field(description="UUID of the address type klasse.")
    employee_uuid: Optional[UUID] = Field(
        description="UUID of the employee related to the address."
    )
    org_unit_uuid: Optional[UUID] = Field(
        description="UUID of the organisation unit related to the address."
    )
    engagement_uuid: Optional[UUID] = Field(
        description="UUID of the engagement related to the address."
    )
    visibility_uuid: Optional[UUID] = Field(
        description="UUID of the visibility klasse of the address."
    )

    # NOTE: The one and only one of {employee, org_unit, engagement} invariant
    # is not validated here because reads are assumed to originate from valid data.


class AddressWrite(AddressBase):
    """
    A MO address write object.
    Note that one and only one of {employee, org_unit, engagement} can be given.
    """

    address_type: AddressType = Field(
        description="Reference to the address type klasse."
    )
    employee: Optional[EmployeeRef] = Field(
        description="Reference to the employee for which the address should be created."
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description=(
            "Reference to the organisation unit for which the address should "
            "be created."
        )
    )
    engagement: Optional[EngagementRef] = Field(
        description=(
            "Reference to the engagement for which the address should be created."
        )
    )
    visibility: Optional[Visibility] = Field(
        description="Reference to the Visibility klasse of the created address object."
    )

    # NOTE: This is not optimal handling of variability. In a perfect world,
    # we'd have an object_ref: Union[EmployeeRef, OrgUnitRef, EngagementRef]
    # field so that we do not have to check it like this.
    @root_validator
    def validate_references(cls, values: DictStrAny) -> DictStrAny:
        references = (
            values.get("employee"),
            values.get("org_unit"),
            values.get("engagement"),
        )
        too_short = ValueError("A reference must be specified")
        too_long = ValueError("Too many references specified.")
        one(
            filter(lambda ref: ref is not None, references),
            too_short=too_short,
            too_long=too_long,
        )

        return values


class AddressDetail(AddressWrite, Details):
    @root_validator
    def validate_references(cls, values: DictStrAny) -> DictStrAny:
        """Reference validator is overwritten because all refs are optional."""
        return values


class Address(MOBase):
    """
    A MO address object.
    """

    type_: Literal["address"] = Field(
        "address", alias="type", description="The object type."
    )
    value: str = Field(description="Value of the address, e.g. street or phone number.")
    value2: Optional[str] = Field(description="Optional second value of the address.")
    address_type: AddressType = Field(
        description="Reference to the address type facet."
    )
    org: Optional[OrganisationRef] = Field(
        description=(
            "Reference to the organisation under which the address should be created. "
            "MO only supports one organisation, so this is rarely used."
        )
    )
    person: Optional[PersonRef] = Field(
        description=(
            "Reference to the person object for which the address should be created."
        )
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description=(
            "Reference to the organisation unit for which the address should be "
            "created."
        )
    )
    engagement: Optional[EngagementRef] = Field(
        description=(
            "Reference to the engagement for which the address should be created."
        )
    )
    validity: Validity = Field(description="Validity of the created address object.")
    visibility: Optional[Visibility] = Field(
        description="Reference to the Visibility klasse of the created address object."
    )

    @classmethod
    def from_simplified_fields(
        cls,
        value: str,
        address_type_uuid: UUID,
        from_date: str,
        uuid: Optional[UUID] = None,
        to_date: Optional[str] = None,
        value2: Optional[str] = None,
        person_uuid: Optional[UUID] = None,
        org_unit_uuid: Optional[UUID] = None,
        engagement_uuid: Optional[UUID] = None,
        visibility_uuid: Optional[UUID] = None,
        org_uuid: Optional[UUID] = None,
    ) -> "Address":
        """Create an address from simplified fields."""
        address_type = AddressType(uuid=address_type_uuid)
        org = OrganisationRef(uuid=org_uuid) if org_uuid else None
        validity = Validity(from_date=from_date, to_date=to_date)
        person = PersonRef(uuid=person_uuid) if person_uuid else None
        org_unit = OrgUnitRef(uuid=org_unit_uuid) if org_unit_uuid else None
        engagement = EngagementRef(uuid=engagement_uuid) if engagement_uuid else None
        visibility = Visibility(uuid=visibility_uuid) if visibility_uuid else None
        return cls(
            uuid=uuid,
            value=value,
            value2=value2,
            address_type=address_type,
            org=org,
            person=person,
            org_unit=org_unit,
            engagement=engagement,
            visibility=visibility,
            validity=validity,
        )
