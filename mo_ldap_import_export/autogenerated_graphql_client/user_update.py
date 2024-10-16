from uuid import UUID

from .base_model import BaseModel


class UserUpdate(BaseModel):
    employee_update: "UserUpdateEmployeeUpdate"


class UserUpdateEmployeeUpdate(BaseModel):
    uuid: UUID


UserUpdate.update_forward_refs()
UserUpdateEmployeeUpdate.update_forward_refs()
