from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class TestingClassRead(BaseModel):
    classes: "TestingClassReadClasses"


class TestingClassReadClasses(BaseModel):
    objects: list["TestingClassReadClassesObjects"]


class TestingClassReadClassesObjects(BaseModel):
    validities: list["TestingClassReadClassesObjectsValidities"]


class TestingClassReadClassesObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    scope: str | None
    owner: UUID | None
    published: str | None
    facet: "TestingClassReadClassesObjectsValiditiesFacet"
    parent: Optional["TestingClassReadClassesObjectsValiditiesParent"]
    it_system: Optional["TestingClassReadClassesObjectsValiditiesItSystem"]
    validity: "TestingClassReadClassesObjectsValiditiesValidity"


class TestingClassReadClassesObjectsValiditiesFacet(BaseModel):
    uuid: UUID


class TestingClassReadClassesObjectsValiditiesParent(BaseModel):
    uuid: UUID


class TestingClassReadClassesObjectsValiditiesItSystem(BaseModel):
    uuid: UUID


class TestingClassReadClassesObjectsValiditiesValidity(BaseModel):
    from_: datetime | None = Field(alias="from")
    to: datetime | None


TestingClassRead.update_forward_refs()
TestingClassReadClasses.update_forward_refs()
TestingClassReadClassesObjects.update_forward_refs()
TestingClassReadClassesObjectsValidities.update_forward_refs()
TestingClassReadClassesObjectsValiditiesFacet.update_forward_refs()
TestingClassReadClassesObjectsValiditiesParent.update_forward_refs()
TestingClassReadClassesObjectsValiditiesItSystem.update_forward_refs()
TestingClassReadClassesObjectsValiditiesValidity.update_forward_refs()
