from uuid import UUID

from .base_model import BaseModel
from .fragments import AddressValidityFields


class ReadOrgUnitAddresses(BaseModel):
    addresses: "ReadOrgUnitAddressesAddresses"


class ReadOrgUnitAddressesAddresses(BaseModel):
    objects: list["ReadOrgUnitAddressesAddressesObjects"]


class ReadOrgUnitAddressesAddressesObjects(BaseModel):
    uuid: UUID
    validities: list["ReadOrgUnitAddressesAddressesObjectsValidities"]


class ReadOrgUnitAddressesAddressesObjectsValidities(AddressValidityFields):
    pass


ReadOrgUnitAddresses.update_forward_refs()
ReadOrgUnitAddressesAddresses.update_forward_refs()
ReadOrgUnitAddressesAddressesObjects.update_forward_refs()
ReadOrgUnitAddressesAddressesObjectsValidities.update_forward_refs()
