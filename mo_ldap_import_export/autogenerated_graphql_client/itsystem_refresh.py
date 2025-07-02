from uuid import UUID

from .base_model import BaseModel


class ItsystemRefresh(BaseModel):
    itsystem_refresh: "ItsystemRefreshItsystemRefresh"


class ItsystemRefreshItsystemRefresh(BaseModel):
    objects: list[UUID]


ItsystemRefresh.update_forward_refs()
ItsystemRefreshItsystemRefresh.update_forward_refs()
