from typing import List
from uuid import UUID

from .base_model import BaseModel


class PersonAddressRefresh(BaseModel):
    address_refresh: "PersonAddressRefreshAddressRefresh"


class PersonAddressRefreshAddressRefresh(BaseModel):
    objects: List[UUID]


PersonAddressRefresh.update_forward_refs()
PersonAddressRefreshAddressRefresh.update_forward_refs()
