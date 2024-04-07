from typing import List
from typing import Optional

from .base_model import BaseModel


class ReadClassNameByFacetAndClassUserKey(BaseModel):
    classes: "ReadClassNameByFacetAndClassUserKeyClasses"


class ReadClassNameByFacetAndClassUserKeyClasses(BaseModel):
    objects: List["ReadClassNameByFacetAndClassUserKeyClassesObjects"]


class ReadClassNameByFacetAndClassUserKeyClassesObjects(BaseModel):
    current: Optional["ReadClassNameByFacetAndClassUserKeyClassesObjectsCurrent"]


class ReadClassNameByFacetAndClassUserKeyClassesObjectsCurrent(BaseModel):
    name: str


ReadClassNameByFacetAndClassUserKey.update_forward_refs()
ReadClassNameByFacetAndClassUserKeyClasses.update_forward_refs()
ReadClassNameByFacetAndClassUserKeyClassesObjects.update_forward_refs()
ReadClassNameByFacetAndClassUserKeyClassesObjectsCurrent.update_forward_refs()
