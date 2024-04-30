from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class ReadAddresses(BaseModel):
    addresses: "ReadAddressesAddresses"


class ReadAddressesAddresses(BaseModel):
    objects: List["ReadAddressesAddressesObjects"]


class ReadAddressesAddressesObjects(BaseModel):
    validities: List["ReadAddressesAddressesObjectsValidities"]


class ReadAddressesAddressesObjectsValidities(BaseModel):
    value: Optional[str]
    value2: Optional[str]
    uuid: UUID
    visibility_uuid: Optional[UUID]
    employee_uuid: Optional[UUID]
    org_unit_uuid: Optional[UUID]
    engagement_uuid: Optional[UUID]
    person: Optional[List["ReadAddressesAddressesObjectsValiditiesPerson"]]
    validity: "ReadAddressesAddressesObjectsValiditiesValidity"
    address_type: "ReadAddressesAddressesObjectsValiditiesAddressType"


class ReadAddressesAddressesObjectsValiditiesPerson(BaseModel):
    cpr_no: Optional[CPRNumber]


class ReadAddressesAddressesObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class ReadAddressesAddressesObjectsValiditiesAddressType(BaseModel):
    user_key: str
    uuid: UUID


ReadAddresses.update_forward_refs()
ReadAddressesAddresses.update_forward_refs()
ReadAddressesAddressesObjects.update_forward_refs()
ReadAddressesAddressesObjectsValidities.update_forward_refs()
ReadAddressesAddressesObjectsValiditiesPerson.update_forward_refs()
ReadAddressesAddressesObjectsValiditiesValidity.update_forward_refs()
ReadAddressesAddressesObjectsValiditiesAddressType.update_forward_refs()
