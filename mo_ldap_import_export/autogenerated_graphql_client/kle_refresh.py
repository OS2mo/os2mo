from uuid import UUID

from .base_model import BaseModel


class KleRefresh(BaseModel):
    kle_refresh: "KleRefreshKleRefresh"


class KleRefreshKleRefresh(BaseModel):
    objects: list[UUID]


KleRefresh.update_forward_refs()
KleRefreshKleRefresh.update_forward_refs()
