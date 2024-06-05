from uuid import UUID

from .base_model import BaseModel


class TestingUserCreate(BaseModel):
    employee_create: "TestingUserCreateEmployeeCreate"


class TestingUserCreateEmployeeCreate(BaseModel):
    uuid: UUID


TestingUserCreate.update_forward_refs()
TestingUserCreateEmployeeCreate.update_forward_refs()
