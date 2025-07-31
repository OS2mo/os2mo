from uuid import UUID

from .base_model import BaseModel


class OwnerRefresh(BaseModel):
    owner_refresh: "OwnerRefreshOwnerRefresh"


class OwnerRefreshOwnerRefresh(BaseModel):
    objects: list[UUID]


OwnerRefresh.update_forward_refs()
OwnerRefreshOwnerRefresh.update_forward_refs()
