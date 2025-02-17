from uuid import UUID

from .base_model import BaseModel


class TestingManagerCreate(BaseModel):
    manager_create: "TestingManagerCreateManagerCreate"


class TestingManagerCreateManagerCreate(BaseModel):
    uuid: UUID


TestingManagerCreate.update_forward_refs()
TestingManagerCreateManagerCreate.update_forward_refs()
