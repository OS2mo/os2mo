from uuid import UUID

from .base_model import BaseModel


class AddressTerminate(BaseModel):
    address_terminate: "AddressTerminateAddressTerminate"


class AddressTerminateAddressTerminate(BaseModel):
    uuid: UUID


AddressTerminate.update_forward_refs()
AddressTerminateAddressTerminate.update_forward_refs()
