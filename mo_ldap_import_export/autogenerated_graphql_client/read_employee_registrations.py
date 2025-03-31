from uuid import UUID

from .base_model import BaseModel


class ReadEmployeeRegistrations(BaseModel):
    employees: "ReadEmployeeRegistrationsEmployees"


class ReadEmployeeRegistrationsEmployees(BaseModel):
    objects: list["ReadEmployeeRegistrationsEmployeesObjects"]


class ReadEmployeeRegistrationsEmployeesObjects(BaseModel):
    registrations: list["ReadEmployeeRegistrationsEmployeesObjectsRegistrations"]


class ReadEmployeeRegistrationsEmployeesObjectsRegistrations(BaseModel):
    uuid: UUID


ReadEmployeeRegistrations.update_forward_refs()
ReadEmployeeRegistrationsEmployees.update_forward_refs()
ReadEmployeeRegistrationsEmployeesObjects.update_forward_refs()
ReadEmployeeRegistrationsEmployeesObjectsRegistrations.update_forward_refs()
