from uuid import UUID

from .base_model import BaseModel


class RolebindingRefresh(BaseModel):
    rolebinding_refresh: "RolebindingRefreshRolebindingRefresh"


class RolebindingRefreshRolebindingRefresh(BaseModel):
    objects: list[UUID]


RolebindingRefresh.update_forward_refs()
RolebindingRefreshRolebindingRefresh.update_forward_refs()
