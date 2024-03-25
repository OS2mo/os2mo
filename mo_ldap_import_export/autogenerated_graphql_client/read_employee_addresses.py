from typing import List
from uuid import UUID

from .base_model import BaseModel


class ReadEmployeeAddresses(BaseModel):
    addresses: "ReadEmployeeAddressesAddresses"


class ReadEmployeeAddressesAddresses(BaseModel):
    objects: List["ReadEmployeeAddressesAddressesObjects"]


class ReadEmployeeAddressesAddressesObjects(BaseModel):
    uuid: UUID


ReadEmployeeAddresses.update_forward_refs()
ReadEmployeeAddressesAddresses.update_forward_refs()
ReadEmployeeAddressesAddressesObjects.update_forward_refs()
