from typing import List

from .base_model import BaseModel
from .fragments import AddressValidityFields


class ReadAddresses(BaseModel):
    addresses: "ReadAddressesAddresses"


class ReadAddressesAddresses(BaseModel):
    objects: List["ReadAddressesAddressesObjects"]


class ReadAddressesAddressesObjects(BaseModel):
    validities: List["ReadAddressesAddressesObjectsValidities"]


class ReadAddressesAddressesObjectsValidities(AddressValidityFields):
    pass


ReadAddresses.update_forward_refs()
ReadAddressesAddresses.update_forward_refs()
ReadAddressesAddressesObjects.update_forward_refs()
ReadAddressesAddressesObjectsValidities.update_forward_refs()
