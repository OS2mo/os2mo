from uuid import UUID

from .base_model import BaseModel


class TestingItuserUpdate(BaseModel):
    ituser_update: "TestingItuserUpdateItuserUpdate"


class TestingItuserUpdateItuserUpdate(BaseModel):
    uuid: UUID


TestingItuserUpdate.update_forward_refs()
TestingItuserUpdateItuserUpdate.update_forward_refs()
