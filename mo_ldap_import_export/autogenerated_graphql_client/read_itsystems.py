from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadItsystems(BaseModel):
    itsystems: "ReadItsystemsItsystems"


class ReadItsystemsItsystems(BaseModel):
    objects: list["ReadItsystemsItsystemsObjects"]


class ReadItsystemsItsystemsObjects(BaseModel):
    validities: list["ReadItsystemsItsystemsObjectsValidities"]


class ReadItsystemsItsystemsObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    validity: "ReadItsystemsItsystemsObjectsValiditiesValidity"
    roles: list["ReadItsystemsItsystemsObjectsValiditiesRoles"]


class ReadItsystemsItsystemsObjectsValiditiesValidity(BaseModel):
    from_: datetime | None = Field(alias="from")
    to: datetime | None


class ReadItsystemsItsystemsObjectsValiditiesRoles(BaseModel):
    uuid: UUID


ReadItsystems.update_forward_refs()
ReadItsystemsItsystems.update_forward_refs()
ReadItsystemsItsystemsObjects.update_forward_refs()
ReadItsystemsItsystemsObjectsValidities.update_forward_refs()
ReadItsystemsItsystemsObjectsValiditiesValidity.update_forward_refs()
ReadItsystemsItsystemsObjectsValiditiesRoles.update_forward_refs()
