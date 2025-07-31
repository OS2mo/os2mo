from uuid import UUID

from .base_model import BaseModel


class AddressRefresh(BaseModel):
    address_refresh: "AddressRefreshAddressRefresh"


class AddressRefreshAddressRefresh(BaseModel):
    objects: list[UUID]


AddressRefresh.update_forward_refs()
AddressRefreshAddressRefresh.update_forward_refs()
