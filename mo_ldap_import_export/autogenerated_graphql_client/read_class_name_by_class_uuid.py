from typing import Optional

from .base_model import BaseModel


class ReadClassNameByClassUuid(BaseModel):
    classes: "ReadClassNameByClassUuidClasses"


class ReadClassNameByClassUuidClasses(BaseModel):
    objects: list["ReadClassNameByClassUuidClassesObjects"]


class ReadClassNameByClassUuidClassesObjects(BaseModel):
    current: Optional["ReadClassNameByClassUuidClassesObjectsCurrent"]


class ReadClassNameByClassUuidClassesObjectsCurrent(BaseModel):
    name: str


ReadClassNameByClassUuid.update_forward_refs()
ReadClassNameByClassUuidClasses.update_forward_refs()
ReadClassNameByClassUuidClassesObjects.update_forward_refs()
ReadClassNameByClassUuidClassesObjectsCurrent.update_forward_refs()
