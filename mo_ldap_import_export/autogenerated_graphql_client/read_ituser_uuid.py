from uuid import UUID

from .base_model import BaseModel


class ReadItuserUuid(BaseModel):
    itusers: "ReadItuserUuidItusers"


class ReadItuserUuidItusers(BaseModel):
    objects: list["ReadItuserUuidItusersObjects"]


class ReadItuserUuidItusersObjects(BaseModel):
    uuid: UUID


ReadItuserUuid.update_forward_refs()
ReadItuserUuidItusers.update_forward_refs()
ReadItuserUuidItusersObjects.update_forward_refs()
