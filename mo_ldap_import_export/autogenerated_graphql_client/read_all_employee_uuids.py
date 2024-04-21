from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadAllEmployeeUuids(BaseModel):
    employees: "ReadAllEmployeeUuidsEmployees"


class ReadAllEmployeeUuidsEmployees(BaseModel):
    objects: List["ReadAllEmployeeUuidsEmployeesObjects"]
    page_info: "ReadAllEmployeeUuidsEmployeesPageInfo"


class ReadAllEmployeeUuidsEmployeesObjects(BaseModel):
    validities: List["ReadAllEmployeeUuidsEmployeesObjectsValidities"]


class ReadAllEmployeeUuidsEmployeesObjectsValidities(BaseModel):
    uuid: UUID
    validity: "ReadAllEmployeeUuidsEmployeesObjectsValiditiesValidity"


class ReadAllEmployeeUuidsEmployeesObjectsValiditiesValidity(BaseModel):
    from_: Optional[datetime] = Field(alias="from")
    to: Optional[datetime]


class ReadAllEmployeeUuidsEmployeesPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllEmployeeUuids.update_forward_refs()
ReadAllEmployeeUuidsEmployees.update_forward_refs()
ReadAllEmployeeUuidsEmployeesObjects.update_forward_refs()
ReadAllEmployeeUuidsEmployeesObjectsValidities.update_forward_refs()
ReadAllEmployeeUuidsEmployeesObjectsValiditiesValidity.update_forward_refs()
ReadAllEmployeeUuidsEmployeesPageInfo.update_forward_refs()
