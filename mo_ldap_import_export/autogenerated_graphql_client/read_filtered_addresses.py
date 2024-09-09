from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadFilteredAddresses(BaseModel):
    addresses: "ReadFilteredAddressesAddresses"


class ReadFilteredAddressesAddresses(BaseModel):
    objects: list["ReadFilteredAddressesAddressesObjects"]


class ReadFilteredAddressesAddressesObjects(BaseModel):
    validities: list["ReadFilteredAddressesAddressesObjectsValidities"]


class ReadFilteredAddressesAddressesObjectsValidities(BaseModel):
    address_type: "ReadFilteredAddressesAddressesObjectsValiditiesAddressType"
    uuid: UUID
    validity: "ReadFilteredAddressesAddressesObjectsValiditiesValidity"


class ReadFilteredAddressesAddressesObjectsValiditiesAddressType(BaseModel):
    user_key: str


class ReadFilteredAddressesAddressesObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadFilteredAddresses.update_forward_refs()
ReadFilteredAddressesAddresses.update_forward_refs()
ReadFilteredAddressesAddressesObjects.update_forward_refs()
ReadFilteredAddressesAddressesObjectsValidities.update_forward_refs()
ReadFilteredAddressesAddressesObjectsValiditiesAddressType.update_forward_refs()
ReadFilteredAddressesAddressesObjectsValiditiesValidity.update_forward_refs()
