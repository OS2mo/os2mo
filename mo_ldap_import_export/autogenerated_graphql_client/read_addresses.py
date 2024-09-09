from .base_model import BaseModel
from .fragments import AddressValidityFields


class ReadAddresses(BaseModel):
    addresses: "ReadAddressesAddresses"


class ReadAddressesAddresses(BaseModel):
    objects: list["ReadAddressesAddressesObjects"]


class ReadAddressesAddressesObjects(BaseModel):
    validities: list["ReadAddressesAddressesObjectsValidities"]


class ReadAddressesAddressesObjectsValidities(AddressValidityFields):
    pass


ReadAddresses.update_forward_refs()
ReadAddressesAddresses.update_forward_refs()
ReadAddressesAddressesObjects.update_forward_refs()
ReadAddressesAddressesObjectsValidities.update_forward_refs()
