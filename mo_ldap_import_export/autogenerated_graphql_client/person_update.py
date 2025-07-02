from uuid import UUID

from .base_model import BaseModel


class PersonUpdate(BaseModel):
    employee_update: "PersonUpdateEmployeeUpdate"


class PersonUpdateEmployeeUpdate(BaseModel):
    uuid: UUID


PersonUpdate.update_forward_refs()
PersonUpdateEmployeeUpdate.update_forward_refs()
