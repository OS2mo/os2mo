from typing import List
from uuid import UUID

from .base_model import BaseModel


class EngagementOrgUnitAddressRefresh(BaseModel):
    address_refresh: "EngagementOrgUnitAddressRefreshAddressRefresh"


class EngagementOrgUnitAddressRefreshAddressRefresh(BaseModel):
    objects: List[UUID]


EngagementOrgUnitAddressRefresh.update_forward_refs()
EngagementOrgUnitAddressRefreshAddressRefresh.update_forward_refs()
