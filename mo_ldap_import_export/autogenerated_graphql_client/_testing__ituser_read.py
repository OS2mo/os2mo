from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class TestingItuserRead(BaseModel):
    itusers: "TestingItuserReadItusers"


class TestingItuserReadItusers(BaseModel):
    objects: list["TestingItuserReadItusersObjects"]


class TestingItuserReadItusersObjects(BaseModel):
    validities: list["TestingItuserReadItusersObjectsValidities"]


class TestingItuserReadItusersObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    itsystem: "TestingItuserReadItusersObjectsValiditiesItsystem"
    person: list["TestingItuserReadItusersObjectsValiditiesPerson"] | None
    validity: "TestingItuserReadItusersObjectsValiditiesValidity"


class TestingItuserReadItusersObjectsValiditiesItsystem(BaseModel):
    user_key: str


class TestingItuserReadItusersObjectsValiditiesPerson(BaseModel):
    uuid: UUID


class TestingItuserReadItusersObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


TestingItuserRead.update_forward_refs()
TestingItuserReadItusers.update_forward_refs()
TestingItuserReadItusersObjects.update_forward_refs()
TestingItuserReadItusersObjectsValidities.update_forward_refs()
TestingItuserReadItusersObjectsValiditiesItsystem.update_forward_refs()
TestingItuserReadItusersObjectsValiditiesPerson.update_forward_refs()
TestingItuserReadItusersObjectsValiditiesValidity.update_forward_refs()
