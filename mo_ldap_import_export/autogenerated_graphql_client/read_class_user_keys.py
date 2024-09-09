from typing import Optional

from .base_model import BaseModel


class ReadClassUserKeys(BaseModel):
    classes: "ReadClassUserKeysClasses"


class ReadClassUserKeysClasses(BaseModel):
    objects: list["ReadClassUserKeysClassesObjects"]


class ReadClassUserKeysClassesObjects(BaseModel):
    current: Optional["ReadClassUserKeysClassesObjectsCurrent"]


class ReadClassUserKeysClassesObjectsCurrent(BaseModel):
    user_key: str


ReadClassUserKeys.update_forward_refs()
ReadClassUserKeysClasses.update_forward_refs()
ReadClassUserKeysClassesObjects.update_forward_refs()
ReadClassUserKeysClassesObjectsCurrent.update_forward_refs()
