from datetime import datetime
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class ReadEmployees(BaseModel):
    employees: "ReadEmployeesEmployees"


class ReadEmployeesEmployees(BaseModel):
    objects: list["ReadEmployeesEmployeesObjects"]


class ReadEmployeesEmployeesObjects(BaseModel):
    validities: list["ReadEmployeesEmployeesObjectsValidities"]


class ReadEmployeesEmployeesObjectsValidities(BaseModel):
    uuid: UUID
    cpr_no: CPRNumber | None
    givenname: str
    surname: str
    nickname_givenname: str | None
    nickname_surname: str | None
    validity: "ReadEmployeesEmployeesObjectsValiditiesValidity"


class ReadEmployeesEmployeesObjectsValiditiesValidity(BaseModel):
    to: datetime | None
    from_: datetime | None = Field(alias="from")


ReadEmployees.update_forward_refs()
ReadEmployeesEmployees.update_forward_refs()
ReadEmployeesEmployeesObjects.update_forward_refs()
ReadEmployeesEmployeesObjectsValidities.update_forward_refs()
ReadEmployeesEmployeesObjectsValiditiesValidity.update_forward_refs()
