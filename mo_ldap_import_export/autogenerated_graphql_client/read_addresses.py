from datetime import datetime
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class ReadAddresses(BaseModel):
    addresses: "ReadAddressesAddresses"


class ReadAddressesAddresses(BaseModel):
    objects: list["ReadAddressesAddressesObjects"]


class ReadAddressesAddressesObjects(BaseModel):
    validities: list["ReadAddressesAddressesObjectsValidities"]


class ReadAddressesAddressesObjectsValidities(BaseModel):
    value: str | None
    value2: str | None
    uuid: UUID
    visibility_uuid: UUID | None
    employee_uuid: UUID | None
    org_unit_uuid: UUID | None
    engagement_uuid: UUID | None
    person: list["ReadAddressesAddressesObjectsValiditiesPerson"] | None
    validity: "ReadAddressesAddressesObjectsValiditiesValidity"
    address_type: "ReadAddressesAddressesObjectsValiditiesAddressType"


class ReadAddressesAddressesObjectsValiditiesPerson(BaseModel):
    cpr_number: CPRNumber | None


class ReadAddressesAddressesObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


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
