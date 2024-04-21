from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadAllItuserUuids(BaseModel):
    itusers: "ReadAllItuserUuidsItusers"


class ReadAllItuserUuidsItusers(BaseModel):
    objects: List["ReadAllItuserUuidsItusersObjects"]
    page_info: "ReadAllItuserUuidsItusersPageInfo"


class ReadAllItuserUuidsItusersObjects(BaseModel):
    validities: List["ReadAllItuserUuidsItusersObjectsValidities"]


class ReadAllItuserUuidsItusersObjectsValidities(BaseModel):
    uuid: UUID
    org_unit_uuid: Optional[UUID]
    employee_uuid: Optional[UUID]
    validity: "ReadAllItuserUuidsItusersObjectsValiditiesValidity"


class ReadAllItuserUuidsItusersObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class ReadAllItuserUuidsItusersPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllItuserUuids.update_forward_refs()
ReadAllItuserUuidsItusers.update_forward_refs()
ReadAllItuserUuidsItusersObjects.update_forward_refs()
ReadAllItuserUuidsItusersObjectsValidities.update_forward_refs()
ReadAllItuserUuidsItusersObjectsValiditiesValidity.update_forward_refs()
ReadAllItuserUuidsItusersPageInfo.update_forward_refs()
