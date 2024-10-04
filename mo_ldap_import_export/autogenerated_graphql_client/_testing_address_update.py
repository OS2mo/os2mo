from uuid import UUID

from .base_model import BaseModel


class TestingAddressUpdate(BaseModel):
    address_update: "TestingAddressUpdateAddressUpdate"


class TestingAddressUpdateAddressUpdate(BaseModel):
    uuid: UUID


TestingAddressUpdate.update_forward_refs()
TestingAddressUpdateAddressUpdate.update_forward_refs()
