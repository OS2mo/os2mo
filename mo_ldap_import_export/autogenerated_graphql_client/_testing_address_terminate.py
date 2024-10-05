from uuid import UUID

from .base_model import BaseModel


class TestingAddressTerminate(BaseModel):
    address_terminate: "TestingAddressTerminateAddressTerminate"


class TestingAddressTerminateAddressTerminate(BaseModel):
    uuid: UUID


TestingAddressTerminate.update_forward_refs()
TestingAddressTerminateAddressTerminate.update_forward_refs()
