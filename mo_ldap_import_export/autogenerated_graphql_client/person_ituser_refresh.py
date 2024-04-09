from typing import List
from uuid import UUID

from .base_model import BaseModel


class PersonItuserRefresh(BaseModel):
    ituser_refresh: "PersonItuserRefreshItuserRefresh"


class PersonItuserRefreshItuserRefresh(BaseModel):
    objects: List[UUID]


PersonItuserRefresh.update_forward_refs()
PersonItuserRefreshItuserRefresh.update_forward_refs()
