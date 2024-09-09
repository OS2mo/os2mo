from uuid import UUID

from .base_model import BaseModel


class ReadItuserByEmployeeAndItsystemUuid(BaseModel):
    itusers: "ReadItuserByEmployeeAndItsystemUuidItusers"


class ReadItuserByEmployeeAndItsystemUuidItusers(BaseModel):
    objects: list["ReadItuserByEmployeeAndItsystemUuidItusersObjects"]


class ReadItuserByEmployeeAndItsystemUuidItusersObjects(BaseModel):
    uuid: UUID


ReadItuserByEmployeeAndItsystemUuid.update_forward_refs()
ReadItuserByEmployeeAndItsystemUuidItusers.update_forward_refs()
ReadItuserByEmployeeAndItsystemUuidItusersObjects.update_forward_refs()
