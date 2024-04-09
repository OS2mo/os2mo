from typing import List
from uuid import UUID

from .base_model import BaseModel


class ItuserRefresh(BaseModel):
    ituser_refresh: "ItuserRefreshItuserRefresh"


class ItuserRefreshItuserRefresh(BaseModel):
    objects: List[UUID]


ItuserRefresh.update_forward_refs()
ItuserRefreshItuserRefresh.update_forward_refs()
