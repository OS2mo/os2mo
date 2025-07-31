from uuid import UUID

from .base_model import BaseModel


class RelatedUnitRefresh(BaseModel):
    related_unit_refresh: "RelatedUnitRefreshRelatedUnitRefresh"


class RelatedUnitRefreshRelatedUnitRefresh(BaseModel):
    objects: list[UUID]


RelatedUnitRefresh.update_forward_refs()
RelatedUnitRefreshRelatedUnitRefresh.update_forward_refs()
