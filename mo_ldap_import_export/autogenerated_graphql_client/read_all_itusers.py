from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadAllItusers(BaseModel):
    itusers: "ReadAllItusersItusers"


class ReadAllItusersItusers(BaseModel):
    objects: List["ReadAllItusersItusersObjects"]
    page_info: "ReadAllItusersItusersPageInfo"


class ReadAllItusersItusersObjects(BaseModel):
    current: Optional["ReadAllItusersItusersObjectsCurrent"]


class ReadAllItusersItusersObjectsCurrent(BaseModel):
    itsystem_uuid: UUID
    employee_uuid: Optional[UUID]
    user_key: str


class ReadAllItusersItusersPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllItusers.update_forward_refs()
ReadAllItusersItusers.update_forward_refs()
ReadAllItusersItusersObjects.update_forward_refs()
ReadAllItusersItusersObjectsCurrent.update_forward_refs()
ReadAllItusersItusersPageInfo.update_forward_refs()
