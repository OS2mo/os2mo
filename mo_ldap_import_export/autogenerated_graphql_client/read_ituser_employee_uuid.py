from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadItuserEmployeeUuid(BaseModel):
    itusers: "ReadItuserEmployeeUuidItusers"


class ReadItuserEmployeeUuidItusers(BaseModel):
    objects: List["ReadItuserEmployeeUuidItusersObjects"]


class ReadItuserEmployeeUuidItusersObjects(BaseModel):
    current: Optional["ReadItuserEmployeeUuidItusersObjectsCurrent"]


class ReadItuserEmployeeUuidItusersObjectsCurrent(BaseModel):
    employee_uuid: Optional[UUID]


ReadItuserEmployeeUuid.update_forward_refs()
ReadItuserEmployeeUuidItusers.update_forward_refs()
ReadItuserEmployeeUuidItusersObjects.update_forward_refs()
ReadItuserEmployeeUuidItusersObjectsCurrent.update_forward_refs()
