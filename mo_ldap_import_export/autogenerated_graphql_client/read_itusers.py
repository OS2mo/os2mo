from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadItusers(BaseModel):
    itusers: "ReadItusersItusers"


class ReadItusersItusers(BaseModel):
    objects: list["ReadItusersItusersObjects"]


class ReadItusersItusersObjects(BaseModel):
    validities: list["ReadItusersItusersObjectsValidities"]


class ReadItusersItusersObjectsValidities(BaseModel):
    user_key: str
    validity: "ReadItusersItusersObjectsValiditiesValidity"
    employee_uuid: UUID | None
    itsystem_uuid: UUID
    engagement_uuids: list[UUID]
    rolebindings: list["ReadItusersItusersObjectsValiditiesRolebindings"]
    external_id: str | None


class ReadItusersItusersObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


class ReadItusersItusersObjectsValiditiesRolebindings(BaseModel):
    uuid: UUID


ReadItusers.update_forward_refs()
ReadItusersItusers.update_forward_refs()
ReadItusersItusersObjects.update_forward_refs()
ReadItusersItusersObjectsValidities.update_forward_refs()
ReadItusersItusersObjectsValiditiesValidity.update_forward_refs()
ReadItusersItusersObjectsValiditiesRolebindings.update_forward_refs()
