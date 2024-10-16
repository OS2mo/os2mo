from uuid import UUID

from .base_model import BaseModel


class UserCreate(BaseModel):
    employee_create: "UserCreateEmployeeCreate"


class UserCreateEmployeeCreate(BaseModel):
    uuid: UUID


UserCreate.update_forward_refs()
UserCreateEmployeeCreate.update_forward_refs()
