from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadFacetUuid(BaseModel):
    facets: "ReadFacetUuidFacets"


class ReadFacetUuidFacets(BaseModel):
    objects: List["ReadFacetUuidFacetsObjects"]


class ReadFacetUuidFacetsObjects(BaseModel):
    current: Optional["ReadFacetUuidFacetsObjectsCurrent"]


class ReadFacetUuidFacetsObjectsCurrent(BaseModel):
    uuid: UUID


ReadFacetUuid.update_forward_refs()
ReadFacetUuidFacets.update_forward_refs()
ReadFacetUuidFacetsObjects.update_forward_refs()
ReadFacetUuidFacetsObjectsCurrent.update_forward_refs()
