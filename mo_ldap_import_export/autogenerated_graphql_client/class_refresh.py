from uuid import UUID

from .base_model import BaseModel


class ClassRefresh(BaseModel):
    class_refresh: "ClassRefreshClassRefresh"


class ClassRefreshClassRefresh(BaseModel):
    objects: list[UUID]


ClassRefresh.update_forward_refs()
ClassRefreshClassRefresh.update_forward_refs()
