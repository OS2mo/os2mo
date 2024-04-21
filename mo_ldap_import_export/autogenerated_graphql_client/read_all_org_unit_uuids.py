from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadAllOrgUnitUuids(BaseModel):
    org_units: "ReadAllOrgUnitUuidsOrgUnits"


class ReadAllOrgUnitUuidsOrgUnits(BaseModel):
    objects: List["ReadAllOrgUnitUuidsOrgUnitsObjects"]
    page_info: "ReadAllOrgUnitUuidsOrgUnitsPageInfo"


class ReadAllOrgUnitUuidsOrgUnitsObjects(BaseModel):
    validities: List["ReadAllOrgUnitUuidsOrgUnitsObjectsValidities"]


class ReadAllOrgUnitUuidsOrgUnitsObjectsValidities(BaseModel):
    uuid: UUID
    validity: "ReadAllOrgUnitUuidsOrgUnitsObjectsValiditiesValidity"


class ReadAllOrgUnitUuidsOrgUnitsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class ReadAllOrgUnitUuidsOrgUnitsPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllOrgUnitUuids.update_forward_refs()
ReadAllOrgUnitUuidsOrgUnits.update_forward_refs()
ReadAllOrgUnitUuidsOrgUnitsObjects.update_forward_refs()
ReadAllOrgUnitUuidsOrgUnitsObjectsValidities.update_forward_refs()
ReadAllOrgUnitUuidsOrgUnitsObjectsValiditiesValidity.update_forward_refs()
ReadAllOrgUnitUuidsOrgUnitsPageInfo.update_forward_refs()
