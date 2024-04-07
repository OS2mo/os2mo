from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadFacetClasses(BaseModel):
    classes: "ReadFacetClassesClasses"


class ReadFacetClassesClasses(BaseModel):
    objects: List["ReadFacetClassesClassesObjects"]


class ReadFacetClassesClassesObjects(BaseModel):
    current: Optional["ReadFacetClassesClassesObjectsCurrent"]


class ReadFacetClassesClassesObjectsCurrent(BaseModel):
    user_key: str
    uuid: UUID
    scope: Optional[str]
    name: str


ReadFacetClasses.update_forward_refs()
ReadFacetClassesClasses.update_forward_refs()
ReadFacetClassesClassesObjects.update_forward_refs()
ReadFacetClassesClassesObjectsCurrent.update_forward_refs()
