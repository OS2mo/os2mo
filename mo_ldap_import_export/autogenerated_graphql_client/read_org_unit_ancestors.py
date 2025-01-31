from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadOrgUnitAncestors(BaseModel):
    org_units: "ReadOrgUnitAncestorsOrgUnits"


class ReadOrgUnitAncestorsOrgUnits(BaseModel):
    objects: list["ReadOrgUnitAncestorsOrgUnitsObjects"]


class ReadOrgUnitAncestorsOrgUnitsObjects(BaseModel):
    current: Optional["ReadOrgUnitAncestorsOrgUnitsObjectsCurrent"]


class ReadOrgUnitAncestorsOrgUnitsObjectsCurrent(BaseModel):
    ancestors: list["ReadOrgUnitAncestorsOrgUnitsObjectsCurrentAncestors"]


class ReadOrgUnitAncestorsOrgUnitsObjectsCurrentAncestors(BaseModel):
    uuid: UUID


ReadOrgUnitAncestors.update_forward_refs()
ReadOrgUnitAncestorsOrgUnits.update_forward_refs()
ReadOrgUnitAncestorsOrgUnitsObjects.update_forward_refs()
ReadOrgUnitAncestorsOrgUnitsObjectsCurrent.update_forward_refs()
ReadOrgUnitAncestorsOrgUnitsObjectsCurrentAncestors.update_forward_refs()
