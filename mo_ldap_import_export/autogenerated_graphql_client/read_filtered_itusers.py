from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadFilteredItusers(BaseModel):
    itusers: "ReadFilteredItusersItusers"


class ReadFilteredItusersItusers(BaseModel):
    objects: list["ReadFilteredItusersItusersObjects"]


class ReadFilteredItusersItusersObjects(BaseModel):
    validities: list["ReadFilteredItusersItusersObjectsValidities"]


class ReadFilteredItusersItusersObjectsValidities(BaseModel):
    employee_uuid: UUID | None
    itsystem: "ReadFilteredItusersItusersObjectsValiditiesItsystem"
    uuid: UUID
    validity: "ReadFilteredItusersItusersObjectsValiditiesValidity"


class ReadFilteredItusersItusersObjectsValiditiesItsystem(BaseModel):
    user_key: str


class ReadFilteredItusersItusersObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadFilteredItusers.update_forward_refs()
ReadFilteredItusersItusers.update_forward_refs()
ReadFilteredItusersItusersObjects.update_forward_refs()
ReadFilteredItusersItusersObjectsValidities.update_forward_refs()
ReadFilteredItusersItusersObjectsValiditiesItsystem.update_forward_refs()
ReadFilteredItusersItusersObjectsValiditiesValidity.update_forward_refs()
