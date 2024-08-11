from typing import List
from uuid import UUID

from .base_model import BaseModel


class ReadOrgUnitUuid(BaseModel):
    org_units: "ReadOrgUnitUuidOrgUnits"


class ReadOrgUnitUuidOrgUnits(BaseModel):
    objects: List["ReadOrgUnitUuidOrgUnitsObjects"]


class ReadOrgUnitUuidOrgUnitsObjects(BaseModel):
    uuid: UUID


ReadOrgUnitUuid.update_forward_refs()
ReadOrgUnitUuidOrgUnits.update_forward_refs()
ReadOrgUnitUuidOrgUnitsObjects.update_forward_refs()
