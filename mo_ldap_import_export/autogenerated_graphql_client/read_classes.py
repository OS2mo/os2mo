from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadClasses(BaseModel):
    classes: "ReadClassesClasses"


class ReadClassesClasses(BaseModel):
    objects: list["ReadClassesClassesObjects"]


class ReadClassesClassesObjects(BaseModel):
    validities: list["ReadClassesClassesObjectsValidities"]


class ReadClassesClassesObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    scope: str | None
    owner: UUID | None
    published: str | None
    facet: "ReadClassesClassesObjectsValiditiesFacet"
    parent: Optional["ReadClassesClassesObjectsValiditiesParent"]
    it_system: Optional["ReadClassesClassesObjectsValiditiesItSystem"]
    validity: "ReadClassesClassesObjectsValiditiesValidity"


class ReadClassesClassesObjectsValiditiesFacet(BaseModel):
    uuid: UUID


class ReadClassesClassesObjectsValiditiesParent(BaseModel):
    uuid: UUID


class ReadClassesClassesObjectsValiditiesItSystem(BaseModel):
    uuid: UUID


class ReadClassesClassesObjectsValiditiesValidity(BaseModel):
    from_: datetime | None = Field(alias="from")
    to: datetime | None


ReadClasses.update_forward_refs()
ReadClassesClasses.update_forward_refs()
ReadClassesClassesObjects.update_forward_refs()
ReadClassesClassesObjectsValidities.update_forward_refs()
ReadClassesClassesObjectsValiditiesFacet.update_forward_refs()
ReadClassesClassesObjectsValiditiesParent.update_forward_refs()
ReadClassesClassesObjectsValiditiesItSystem.update_forward_refs()
ReadClassesClassesObjectsValiditiesValidity.update_forward_refs()
