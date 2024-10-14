from uuid import UUID

from .base_model import BaseModel


class TestingUserUpdate(BaseModel):
    employee_update: "TestingUserUpdateEmployeeUpdate"


class TestingUserUpdateEmployeeUpdate(BaseModel):
    uuid: UUID


TestingUserUpdate.update_forward_refs()
TestingUserUpdateEmployeeUpdate.update_forward_refs()
