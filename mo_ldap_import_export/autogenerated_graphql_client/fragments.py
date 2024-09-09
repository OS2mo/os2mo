from datetime import datetime
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class AddressValidityFields(BaseModel):
    value: str | None
    value2: str | None
    uuid: UUID
    visibility_uuid: UUID | None
    employee_uuid: UUID | None
    org_unit_uuid: UUID | None
    engagement_uuid: UUID | None
    person: list["AddressValidityFieldsPerson"] | None
    validity: "AddressValidityFieldsValidity"
    address_type: "AddressValidityFieldsAddressType"


class AddressValidityFieldsPerson(BaseModel):
    cpr_no: CPRNumber | None


class AddressValidityFieldsValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


class AddressValidityFieldsAddressType(BaseModel):
    user_key: str
    uuid: UUID


AddressValidityFields.update_forward_refs()
AddressValidityFieldsPerson.update_forward_refs()
AddressValidityFieldsValidity.update_forward_refs()
AddressValidityFieldsAddressType.update_forward_refs()
