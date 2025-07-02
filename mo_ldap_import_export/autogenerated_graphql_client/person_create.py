from uuid import UUID

from .base_model import BaseModel


class PersonCreate(BaseModel):
    employee_create: "PersonCreateEmployeeCreate"


class PersonCreateEmployeeCreate(BaseModel):
    uuid: UUID


PersonCreate.update_forward_refs()
PersonCreateEmployeeCreate.update_forward_refs()
