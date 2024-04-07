from typing import List
from uuid import UUID

from .base_model import BaseModel


class ReadClassUuidByFacetAndClassUserKey(BaseModel):
    classes: "ReadClassUuidByFacetAndClassUserKeyClasses"


class ReadClassUuidByFacetAndClassUserKeyClasses(BaseModel):
    objects: List["ReadClassUuidByFacetAndClassUserKeyClassesObjects"]


class ReadClassUuidByFacetAndClassUserKeyClassesObjects(BaseModel):
    uuid: UUID


ReadClassUuidByFacetAndClassUserKey.update_forward_refs()
ReadClassUuidByFacetAndClassUserKeyClasses.update_forward_refs()
ReadClassUuidByFacetAndClassUserKeyClassesObjects.update_forward_refs()
