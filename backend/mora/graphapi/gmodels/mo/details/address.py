# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from pydantic.v1 import Field

from .._shared import MOBase
from .._shared import Validity


class AddressRead(MOBase):
    """
    A MO address read object.
    Note that one and only one of {employee, org_unit} are given at any time.
    """

    type_: str = Field("address", alias="type", description="The object type.")
    value: str = Field(description="Value of the address, e.g. street or phone number.")
    value2: str | None = Field(description="Optional second value of the address.")
    validity: Validity = Field(description="Validity of the address object.")

    address_type_uuid: UUID = Field(description="UUID of the address type klasse.")
    employee_uuid: UUID | None = Field(
        description="UUID of the employee related to the address."
    )
    org_unit_uuid: UUID | None = Field(
        description="UUID of the organisation unit related to the address."
    )
    engagement_uuid: UUID | None = Field(
        description="Optional UUID of an associated engagement."
    )
    visibility_uuid: UUID | None = Field(
        description="UUID of the visibility klasse of the address."
    )

    # NOTE: The one and only one of {employee, org_unit} invariant is not validated
    # here because reads are assumed to originate from valid data.
