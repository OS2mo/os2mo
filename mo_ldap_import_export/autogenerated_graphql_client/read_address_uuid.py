from uuid import UUID

from .base_model import BaseModel


class ReadAddressUuid(BaseModel):
    addresses: "ReadAddressUuidAddresses"


class ReadAddressUuidAddresses(BaseModel):
    objects: list["ReadAddressUuidAddressesObjects"]


class ReadAddressUuidAddressesObjects(BaseModel):
    uuid: UUID


ReadAddressUuid.update_forward_refs()
ReadAddressUuidAddresses.update_forward_refs()
ReadAddressUuidAddressesObjects.update_forward_refs()
