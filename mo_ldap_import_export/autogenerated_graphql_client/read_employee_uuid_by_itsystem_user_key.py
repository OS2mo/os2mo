from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEmployeeUuidByItsystemUserKey(BaseModel):
    itusers: "ReadEmployeeUuidByItsystemUserKeyItusers"


class ReadEmployeeUuidByItsystemUserKeyItusers(BaseModel):
    objects: List["ReadEmployeeUuidByItsystemUserKeyItusersObjects"]


class ReadEmployeeUuidByItsystemUserKeyItusersObjects(BaseModel):
    current: Optional["ReadEmployeeUuidByItsystemUserKeyItusersObjectsCurrent"]


class ReadEmployeeUuidByItsystemUserKeyItusersObjectsCurrent(BaseModel):
    employee_uuid: Optional[UUID]


ReadEmployeeUuidByItsystemUserKey.update_forward_refs()
ReadEmployeeUuidByItsystemUserKeyItusers.update_forward_refs()
ReadEmployeeUuidByItsystemUserKeyItusersObjects.update_forward_refs()
ReadEmployeeUuidByItsystemUserKeyItusersObjectsCurrent.update_forward_refs()
