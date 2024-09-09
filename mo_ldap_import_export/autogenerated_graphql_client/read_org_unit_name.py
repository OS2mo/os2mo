from typing import Optional

from .base_model import BaseModel


class ReadOrgUnitName(BaseModel):
    org_units: "ReadOrgUnitNameOrgUnits"


class ReadOrgUnitNameOrgUnits(BaseModel):
    objects: list["ReadOrgUnitNameOrgUnitsObjects"]


class ReadOrgUnitNameOrgUnitsObjects(BaseModel):
    current: Optional["ReadOrgUnitNameOrgUnitsObjectsCurrent"]


class ReadOrgUnitNameOrgUnitsObjectsCurrent(BaseModel):
    name: str


ReadOrgUnitName.update_forward_refs()
ReadOrgUnitNameOrgUnits.update_forward_refs()
ReadOrgUnitNameOrgUnitsObjects.update_forward_refs()
ReadOrgUnitNameOrgUnitsObjectsCurrent.update_forward_refs()
