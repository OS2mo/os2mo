from uuid import UUID

from .base_model import BaseModel


class EngagementRefresh(BaseModel):
    engagement_refresh: "EngagementRefreshEngagementRefresh"


class EngagementRefreshEngagementRefresh(BaseModel):
    objects: list[UUID]


EngagementRefresh.update_forward_refs()
EngagementRefreshEngagementRefresh.update_forward_refs()
