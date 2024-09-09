from typing import Any
from uuid import UUID

from .base_model import BaseModel


class ReadAllItusers(BaseModel):
    itusers: "ReadAllItusersItusers"


class ReadAllItusersItusers(BaseModel):
    objects: list["ReadAllItusersItusersObjects"]
    page_info: "ReadAllItusersItusersPageInfo"


class ReadAllItusersItusersObjects(BaseModel):
    validities: list["ReadAllItusersItusersObjectsValidities"]


class ReadAllItusersItusersObjectsValidities(BaseModel):
    itsystem_uuid: UUID
    employee_uuid: UUID | None
    user_key: str
    uuid: UUID


class ReadAllItusersItusersPageInfo(BaseModel):
    next_cursor: Any | None


ReadAllItusers.update_forward_refs()
ReadAllItusersItusers.update_forward_refs()
ReadAllItusersItusersObjects.update_forward_refs()
ReadAllItusersItusersObjectsValidities.update_forward_refs()
ReadAllItusersItusersPageInfo.update_forward_refs()
