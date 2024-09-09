from uuid import UUID

from .base_model import BaseModel


class OrgUnitEngagementsRefresh(BaseModel):
    engagement_refresh: "OrgUnitEngagementsRefreshEngagementRefresh"


class OrgUnitEngagementsRefreshEngagementRefresh(BaseModel):
    objects: list[UUID]


OrgUnitEngagementsRefresh.update_forward_refs()
OrgUnitEngagementsRefreshEngagementRefresh.update_forward_refs()
