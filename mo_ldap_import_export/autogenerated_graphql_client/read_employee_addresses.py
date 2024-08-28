from typing import List
from uuid import UUID

from .base_model import BaseModel
from .fragments import AddressValidityFields


class ReadEmployeeAddresses(BaseModel):
    addresses: "ReadEmployeeAddressesAddresses"


class ReadEmployeeAddressesAddresses(BaseModel):
    objects: List["ReadEmployeeAddressesAddressesObjects"]


class ReadEmployeeAddressesAddressesObjects(BaseModel):
    uuid: UUID
    validities: List["ReadEmployeeAddressesAddressesObjectsValidities"]


class ReadEmployeeAddressesAddressesObjectsValidities(AddressValidityFields):
    pass


ReadEmployeeAddresses.update_forward_refs()
ReadEmployeeAddressesAddresses.update_forward_refs()
ReadEmployeeAddressesAddressesObjects.update_forward_refs()
ReadEmployeeAddressesAddressesObjectsValidities.update_forward_refs()
