from typing import List
from uuid import UUID

from .base_model import BaseModel


class PersonEngagementRefresh(BaseModel):
    engagement_refresh: "PersonEngagementRefreshEngagementRefresh"


class PersonEngagementRefreshEngagementRefresh(BaseModel):
    objects: List[UUID]


PersonEngagementRefresh.update_forward_refs()
PersonEngagementRefreshEngagementRefresh.update_forward_refs()
