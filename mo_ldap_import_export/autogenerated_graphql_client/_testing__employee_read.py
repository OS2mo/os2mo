from uuid import UUID

from ..types import CPRNumber
from .base_model import BaseModel


class TestingEmployeeRead(BaseModel):
    employees: "TestingEmployeeReadEmployees"


class TestingEmployeeReadEmployees(BaseModel):
    objects: list["TestingEmployeeReadEmployeesObjects"]


class TestingEmployeeReadEmployeesObjects(BaseModel):
    validities: list["TestingEmployeeReadEmployeesObjectsValidities"]


class TestingEmployeeReadEmployeesObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    cpr_number: CPRNumber | None
    given_name: str
    surname: str
    nickname_given_name: str | None
    nickname_surname: str | None


TestingEmployeeRead.update_forward_refs()
TestingEmployeeReadEmployees.update_forward_refs()
TestingEmployeeReadEmployeesObjects.update_forward_refs()
TestingEmployeeReadEmployeesObjectsValidities.update_forward_refs()
