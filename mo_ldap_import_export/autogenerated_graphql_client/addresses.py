from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class Addresses(BaseModel):
    addresses: "AddressesAddresses"


class AddressesAddresses(BaseModel):
    objects: list["AddressesAddressesObjects"]


class AddressesAddressesObjects(BaseModel):
    uuid: UUID
    current: Optional["AddressesAddressesObjectsCurrent"]


class AddressesAddressesObjectsCurrent(BaseModel):
    ituser_uuid: UUID | None


Addresses.update_forward_refs()
AddressesAddresses.update_forward_refs()
AddressesAddressesObjects.update_forward_refs()
AddressesAddressesObjectsCurrent.update_forward_refs()
