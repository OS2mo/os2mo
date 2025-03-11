from uuid import UUID

from .base_model import BaseModel


class ReadItuserRelationUuids(BaseModel):
    itusers: "ReadItuserRelationUuidsItusers"


class ReadItuserRelationUuidsItusers(BaseModel):
    objects: list["ReadItuserRelationUuidsItusersObjects"]


class ReadItuserRelationUuidsItusersObjects(BaseModel):
    validities: list["ReadItuserRelationUuidsItusersObjectsValidities"]


class ReadItuserRelationUuidsItusersObjectsValidities(BaseModel):
    employee_uuid: UUID | None
    org_unit_uuid: UUID | None


ReadItuserRelationUuids.update_forward_refs()
ReadItuserRelationUuidsItusers.update_forward_refs()
ReadItuserRelationUuidsItusersObjects.update_forward_refs()
ReadItuserRelationUuidsItusersObjectsValidities.update_forward_refs()
