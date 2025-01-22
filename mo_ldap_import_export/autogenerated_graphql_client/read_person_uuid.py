from uuid import UUID

from .base_model import BaseModel


class ReadPersonUuid(BaseModel):
    employees: "ReadPersonUuidEmployees"


class ReadPersonUuidEmployees(BaseModel):
    objects: list["ReadPersonUuidEmployeesObjects"]


class ReadPersonUuidEmployeesObjects(BaseModel):
    uuid: UUID


ReadPersonUuid.update_forward_refs()
ReadPersonUuidEmployees.update_forward_refs()
ReadPersonUuidEmployeesObjects.update_forward_refs()
