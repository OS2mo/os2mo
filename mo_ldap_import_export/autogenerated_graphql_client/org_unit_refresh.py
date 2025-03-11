from uuid import UUID

from .base_model import BaseModel


class OrgUnitRefresh(BaseModel):
    org_unit_refresh: "OrgUnitRefreshOrgUnitRefresh"


class OrgUnitRefreshOrgUnitRefresh(BaseModel):
    objects: list[UUID]


OrgUnitRefresh.update_forward_refs()
OrgUnitRefreshOrgUnitRefresh.update_forward_refs()
