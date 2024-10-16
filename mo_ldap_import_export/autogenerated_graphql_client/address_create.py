from uuid import UUID

from .base_model import BaseModel


class AddressCreate(BaseModel):
    address_create: "AddressCreateAddressCreate"


class AddressCreateAddressCreate(BaseModel):
    uuid: UUID


AddressCreate.update_forward_refs()
AddressCreateAddressCreate.update_forward_refs()
