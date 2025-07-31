from uuid import UUID

from .base_model import BaseModel


class ManagerRefresh(BaseModel):
    manager_refresh: "ManagerRefreshManagerRefresh"


class ManagerRefreshManagerRefresh(BaseModel):
    objects: list[UUID]


ManagerRefresh.update_forward_refs()
ManagerRefreshManagerRefresh.update_forward_refs()
