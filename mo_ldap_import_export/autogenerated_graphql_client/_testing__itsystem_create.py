from uuid import UUID

from .base_model import BaseModel


class TestingItsystemCreate(BaseModel):
    itsystem_create: "TestingItsystemCreateItsystemCreate"


class TestingItsystemCreateItsystemCreate(BaseModel):
    uuid: UUID


TestingItsystemCreate.update_forward_refs()
TestingItsystemCreateItsystemCreate.update_forward_refs()
