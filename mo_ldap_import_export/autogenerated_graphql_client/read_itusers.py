from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadItusers(BaseModel):
    itusers: "ReadItusersItusers"


class ReadItusersItusers(BaseModel):
    objects: List["ReadItusersItusersObjects"]


class ReadItusersItusersObjects(BaseModel):
    validities: List["ReadItusersItusersObjectsValidities"]


class ReadItusersItusersObjectsValidities(BaseModel):
    user_key: str
    validity: "ReadItusersItusersObjectsValiditiesValidity"
    employee_uuid: Optional[UUID]
    itsystem_uuid: UUID
    engagement_uuid: Optional[UUID]


class ReadItusersItusersObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


ReadItusers.update_forward_refs()
ReadItusersItusers.update_forward_refs()
ReadItusersItusersObjects.update_forward_refs()
ReadItusersItusersObjectsValidities.update_forward_refs()
ReadItusersItusersObjectsValiditiesValidity.update_forward_refs()
