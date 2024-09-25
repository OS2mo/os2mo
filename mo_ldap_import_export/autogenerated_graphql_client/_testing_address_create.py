from uuid import UUID

from .base_model import BaseModel


class TestingAddressCreate(BaseModel):
    address_create: "TestingAddressCreateAddressCreate"


class TestingAddressCreateAddressCreate(BaseModel):
    uuid: UUID


TestingAddressCreate.update_forward_refs()
TestingAddressCreateAddressCreate.update_forward_refs()
