from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadItsystems(BaseModel):
    itsystems: "ReadItsystemsItsystems"


class ReadItsystemsItsystems(BaseModel):
    objects: List["ReadItsystemsItsystemsObjects"]


class ReadItsystemsItsystemsObjects(BaseModel):
    current: Optional["ReadItsystemsItsystemsObjectsCurrent"]


class ReadItsystemsItsystemsObjectsCurrent(BaseModel):
    uuid: UUID
    user_key: str


ReadItsystems.update_forward_refs()
ReadItsystemsItsystems.update_forward_refs()
ReadItsystemsItsystemsObjects.update_forward_refs()
ReadItsystemsItsystemsObjectsCurrent.update_forward_refs()
