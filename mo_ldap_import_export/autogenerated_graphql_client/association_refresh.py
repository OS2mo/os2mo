from uuid import UUID

from .base_model import BaseModel


class AssociationRefresh(BaseModel):
    association_refresh: "AssociationRefreshAssociationRefresh"


class AssociationRefreshAssociationRefresh(BaseModel):
    objects: list[UUID]


AssociationRefresh.update_forward_refs()
AssociationRefreshAssociationRefresh.update_forward_refs()
