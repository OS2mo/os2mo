from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadFilteredItusers(BaseModel):
    itusers: "ReadFilteredItusersItusers"


class ReadFilteredItusersItusers(BaseModel):
    objects: List["ReadFilteredItusersItusersObjects"]


class ReadFilteredItusersItusersObjects(BaseModel):
    validities: List["ReadFilteredItusersItusersObjectsValidities"]


class ReadFilteredItusersItusersObjectsValidities(BaseModel):
    itsystem: "ReadFilteredItusersItusersObjectsValiditiesItsystem"
    uuid: UUID
    validity: "ReadFilteredItusersItusersObjectsValiditiesValidity"


class ReadFilteredItusersItusersObjectsValiditiesItsystem(BaseModel):
    user_key: str


class ReadFilteredItusersItusersObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


ReadFilteredItusers.update_forward_refs()
ReadFilteredItusersItusers.update_forward_refs()
ReadFilteredItusersItusersObjects.update_forward_refs()
ReadFilteredItusersItusersObjectsValidities.update_forward_refs()
ReadFilteredItusersItusersObjectsValiditiesItsystem.update_forward_refs()
ReadFilteredItusersItusersObjectsValiditiesValidity.update_forward_refs()
