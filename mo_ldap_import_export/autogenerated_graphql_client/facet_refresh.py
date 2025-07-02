from uuid import UUID

from .base_model import BaseModel


class FacetRefresh(BaseModel):
    facet_refresh: "FacetRefreshFacetRefresh"


class FacetRefreshFacetRefresh(BaseModel):
    objects: list[UUID]


FacetRefresh.update_forward_refs()
FacetRefreshFacetRefresh.update_forward_refs()
