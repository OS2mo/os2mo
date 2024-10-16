from uuid import UUID

from .base_model import BaseModel


class AddressUpdate(BaseModel):
    address_update: "AddressUpdateAddressUpdate"


class AddressUpdateAddressUpdate(BaseModel):
    uuid: UUID


AddressUpdate.update_forward_refs()
AddressUpdateAddressUpdate.update_forward_refs()
