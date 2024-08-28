from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class AddressValidityFields(BaseModel):
    value: Optional[str]
    value2: Optional[str]
    uuid: UUID
    visibility_uuid: Optional[UUID]
    employee_uuid: Optional[UUID]
    org_unit_uuid: Optional[UUID]
    engagement_uuid: Optional[UUID]
    person: Optional[List["AddressValidityFieldsPerson"]]
    validity: "AddressValidityFieldsValidity"
    address_type: "AddressValidityFieldsAddressType"


class AddressValidityFieldsPerson(BaseModel):
    cpr_no: Optional[CPRNumber]


class AddressValidityFieldsValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class AddressValidityFieldsAddressType(BaseModel):
    user_key: str
    uuid: UUID


AddressValidityFields.update_forward_refs()
AddressValidityFieldsPerson.update_forward_refs()
AddressValidityFieldsValidity.update_forward_refs()
AddressValidityFieldsAddressType.update_forward_refs()
