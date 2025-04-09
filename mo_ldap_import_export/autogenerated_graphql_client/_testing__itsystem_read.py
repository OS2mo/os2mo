from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class TestingItsystemRead(BaseModel):
    itsystems: "TestingItsystemReadItsystems"


class TestingItsystemReadItsystems(BaseModel):
    objects: list["TestingItsystemReadItsystemsObjects"]


class TestingItsystemReadItsystemsObjects(BaseModel):
    validities: list["TestingItsystemReadItsystemsObjectsValidities"]


class TestingItsystemReadItsystemsObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    validity: "TestingItsystemReadItsystemsObjectsValiditiesValidity"


class TestingItsystemReadItsystemsObjectsValiditiesValidity(BaseModel):
    from_: datetime | None = Field(alias="from")
    to: datetime | None


TestingItsystemRead.update_forward_refs()
TestingItsystemReadItsystems.update_forward_refs()
TestingItsystemReadItsystemsObjects.update_forward_refs()
TestingItsystemReadItsystemsObjectsValidities.update_forward_refs()
TestingItsystemReadItsystemsObjectsValiditiesValidity.update_forward_refs()
