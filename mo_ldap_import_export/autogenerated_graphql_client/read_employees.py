from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEmployees(BaseModel):
    employees: "ReadEmployeesEmployees"


class ReadEmployeesEmployees(BaseModel):
    objects: List["ReadEmployeesEmployeesObjects"]


class ReadEmployeesEmployeesObjects(BaseModel):
    validities: List["ReadEmployeesEmployeesObjectsValidities"]


class ReadEmployeesEmployeesObjectsValidities(BaseModel):
    uuid: UUID
    cpr_no: Optional[str]
    givenname: str
    surname: str
    nickname_givenname: Optional[str]
    nickname_surname: Optional[str]
    validity: "ReadEmployeesEmployeesObjectsValiditiesValidity"


class ReadEmployeesEmployeesObjectsValiditiesValidity(BaseModel):
    to: Optional[datetime]
    from_: Optional[datetime] = Field(alias="from")


ReadEmployees.update_forward_refs()
ReadEmployeesEmployees.update_forward_refs()
ReadEmployeesEmployeesObjects.update_forward_refs()
ReadEmployeesEmployeesObjectsValidities.update_forward_refs()
ReadEmployeesEmployeesObjectsValiditiesValidity.update_forward_refs()
