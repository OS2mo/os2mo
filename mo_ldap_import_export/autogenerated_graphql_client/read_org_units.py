from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadOrgUnits(BaseModel):
    org_units: "ReadOrgUnitsOrgUnits"


class ReadOrgUnitsOrgUnits(BaseModel):
    objects: list["ReadOrgUnitsOrgUnitsObjects"]


class ReadOrgUnitsOrgUnitsObjects(BaseModel):
    validities: list["ReadOrgUnitsOrgUnitsObjectsValidities"]


class ReadOrgUnitsOrgUnitsObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    unit_type: Optional["ReadOrgUnitsOrgUnitsObjectsValiditiesUnitType"]
    validity: "ReadOrgUnitsOrgUnitsObjectsValiditiesValidity"


class ReadOrgUnitsOrgUnitsObjectsValiditiesUnitType(BaseModel):
    uuid: UUID


class ReadOrgUnitsOrgUnitsObjectsValiditiesValidity(BaseModel):
    to: datetime | None
    from_: datetime = Field(alias="from")


ReadOrgUnits.update_forward_refs()
ReadOrgUnitsOrgUnits.update_forward_refs()
ReadOrgUnitsOrgUnitsObjects.update_forward_refs()
ReadOrgUnitsOrgUnitsObjectsValidities.update_forward_refs()
ReadOrgUnitsOrgUnitsObjectsValiditiesUnitType.update_forward_refs()
ReadOrgUnitsOrgUnitsObjectsValiditiesValidity.update_forward_refs()
