from uuid import UUID

from .base_model import BaseModel


class ReadItsystemUuid(BaseModel):
    itsystems: "ReadItsystemUuidItsystems"


class ReadItsystemUuidItsystems(BaseModel):
    objects: list["ReadItsystemUuidItsystemsObjects"]


class ReadItsystemUuidItsystemsObjects(BaseModel):
    uuid: UUID


ReadItsystemUuid.update_forward_refs()
ReadItsystemUuidItsystems.update_forward_refs()
ReadItsystemUuidItsystemsObjects.update_forward_refs()
