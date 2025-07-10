from uuid import UUID

from .base_model import BaseModel


class TestingPersonUpdate(BaseModel):
    employee_update: "TestingPersonUpdateEmployeeUpdate"


class TestingPersonUpdateEmployeeUpdate(BaseModel):
    uuid: UUID


TestingPersonUpdate.update_forward_refs()
TestingPersonUpdateEmployeeUpdate.update_forward_refs()
