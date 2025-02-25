from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadCleanupAddresses(BaseModel):
    addresses: "ReadCleanupAddressesAddresses"


class ReadCleanupAddressesAddresses(BaseModel):
    objects: list["ReadCleanupAddressesAddressesObjects"]


class ReadCleanupAddressesAddressesObjects(BaseModel):
    current: Optional["ReadCleanupAddressesAddressesObjectsCurrent"]


class ReadCleanupAddressesAddressesObjectsCurrent(BaseModel):
    employee_uuid: UUID | None
    uuid: UUID


ReadCleanupAddresses.update_forward_refs()
ReadCleanupAddressesAddresses.update_forward_refs()
ReadCleanupAddressesAddressesObjects.update_forward_refs()
ReadCleanupAddressesAddressesObjectsCurrent.update_forward_refs()
