from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagementsByEmployeeUuids(BaseModel):
    engagements: "ReadEngagementsByEmployeeUuidsEngagements"


class ReadEngagementsByEmployeeUuidsEngagements(BaseModel):
    objects: List["ReadEngagementsByEmployeeUuidsEngagementsObjects"]


class ReadEngagementsByEmployeeUuidsEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementsByEmployeeUuidsEngagementsObjectsCurrent"]


class ReadEngagementsByEmployeeUuidsEngagementsObjectsCurrent(BaseModel):
    uuid: UUID
    validity: "ReadEngagementsByEmployeeUuidsEngagementsObjectsCurrentValidity"


class ReadEngagementsByEmployeeUuidsEngagementsObjectsCurrentValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


ReadEngagementsByEmployeeUuids.update_forward_refs()
ReadEngagementsByEmployeeUuidsEngagements.update_forward_refs()
ReadEngagementsByEmployeeUuidsEngagementsObjects.update_forward_refs()
ReadEngagementsByEmployeeUuidsEngagementsObjectsCurrent.update_forward_refs()
ReadEngagementsByEmployeeUuidsEngagementsObjectsCurrentValidity.update_forward_refs()
