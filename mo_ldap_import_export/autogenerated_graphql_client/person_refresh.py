from uuid import UUID

from .base_model import BaseModel


class PersonRefresh(BaseModel):
    employee_refresh: "PersonRefreshEmployeeRefresh"


class PersonRefreshEmployeeRefresh(BaseModel):
    objects: list[UUID]


PersonRefresh.update_forward_refs()
PersonRefreshEmployeeRefresh.update_forward_refs()
