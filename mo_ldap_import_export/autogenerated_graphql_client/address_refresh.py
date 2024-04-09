from typing import List
from uuid import UUID

from .base_model import BaseModel


class AddressRefresh(BaseModel):
    address_refresh: "AddressRefreshAddressRefresh"


class AddressRefreshAddressRefresh(BaseModel):
    objects: List[UUID]


AddressRefresh.update_forward_refs()
AddressRefreshAddressRefresh.update_forward_refs()
