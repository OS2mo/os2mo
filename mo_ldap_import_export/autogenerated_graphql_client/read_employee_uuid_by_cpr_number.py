from uuid import UUID

from .base_model import BaseModel


class ReadEmployeeUuidByCprNumber(BaseModel):
    employees: "ReadEmployeeUuidByCprNumberEmployees"


class ReadEmployeeUuidByCprNumberEmployees(BaseModel):
    objects: list["ReadEmployeeUuidByCprNumberEmployeesObjects"]


class ReadEmployeeUuidByCprNumberEmployeesObjects(BaseModel):
    uuid: UUID


ReadEmployeeUuidByCprNumber.update_forward_refs()
ReadEmployeeUuidByCprNumberEmployees.update_forward_refs()
ReadEmployeeUuidByCprNumberEmployeesObjects.update_forward_refs()
