from uuid import UUID

from .base_model import BaseModel


class ItuserRefresh(BaseModel):
    ituser_refresh: "ItuserRefreshItuserRefresh"


class ItuserRefreshItuserRefresh(BaseModel):
    objects: list[UUID]


ItuserRefresh.update_forward_refs()
ItuserRefreshItuserRefresh.update_forward_refs()
