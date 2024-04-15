from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadOrgUnits(BaseModel):
    org_units: "ReadOrgUnitsOrgUnits"


class ReadOrgUnitsOrgUnits(BaseModel):
    objects: List["ReadOrgUnitsOrgUnitsObjects"]


class ReadOrgUnitsOrgUnitsObjects(BaseModel):
    uuid: UUID
    validities: List["ReadOrgUnitsOrgUnitsObjectsValidities"]


class ReadOrgUnitsOrgUnitsObjectsValidities(BaseModel):
    uuid: UUID
    name: str
    user_key: str
    parent_uuid: Optional[UUID]
    validity: "ReadOrgUnitsOrgUnitsObjectsValiditiesValidity"


class ReadOrgUnitsOrgUnitsObjectsValiditiesValidity(BaseModel):
    to: Optional[datetime]
    from_: datetime = Field(alias="from")


ReadOrgUnits.update_forward_refs()
ReadOrgUnitsOrgUnits.update_forward_refs()
ReadOrgUnitsOrgUnitsObjects.update_forward_refs()
ReadOrgUnitsOrgUnitsObjectsValidities.update_forward_refs()
ReadOrgUnitsOrgUnitsObjectsValiditiesValidity.update_forward_refs()
