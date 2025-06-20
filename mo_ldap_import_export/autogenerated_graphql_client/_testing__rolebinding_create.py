from uuid import UUID

from .base_model import BaseModel


class TestingRolebindingCreate(BaseModel):
    rolebinding_create: "TestingRolebindingCreateRolebindingCreate"


class TestingRolebindingCreateRolebindingCreate(BaseModel):
    uuid: UUID


TestingRolebindingCreate.update_forward_refs()
TestingRolebindingCreateRolebindingCreate.update_forward_refs()
