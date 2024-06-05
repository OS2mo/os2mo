from uuid import UUID

from .base_model import BaseModel


class TestingItuserCreate(BaseModel):
    ituser_create: "TestingItuserCreateItuserCreate"


class TestingItuserCreateItuserCreate(BaseModel):
    uuid: UUID


TestingItuserCreate.update_forward_refs()
TestingItuserCreateItuserCreate.update_forward_refs()
