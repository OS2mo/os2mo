from typing import List
from uuid import UUID

from .base_model import BaseModel


class ReadClassUuid(BaseModel):
    classes: "ReadClassUuidClasses"


class ReadClassUuidClasses(BaseModel):
    objects: List["ReadClassUuidClassesObjects"]


class ReadClassUuidClassesObjects(BaseModel):
    uuid: UUID


ReadClassUuid.update_forward_refs()
ReadClassUuidClasses.update_forward_refs()
ReadClassUuidClassesObjects.update_forward_refs()
