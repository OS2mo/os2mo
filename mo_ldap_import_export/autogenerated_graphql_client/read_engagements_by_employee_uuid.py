from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagementsByEmployeeUuid(BaseModel):
    engagements: "ReadEngagementsByEmployeeUuidEngagements"


class ReadEngagementsByEmployeeUuidEngagements(BaseModel):
    objects: list["ReadEngagementsByEmployeeUuidEngagementsObjects"]


class ReadEngagementsByEmployeeUuidEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementsByEmployeeUuidEngagementsObjectsCurrent"]


class ReadEngagementsByEmployeeUuidEngagementsObjectsCurrent(BaseModel):
    uuid: UUID
    validity: "ReadEngagementsByEmployeeUuidEngagementsObjectsCurrentValidity"


class ReadEngagementsByEmployeeUuidEngagementsObjectsCurrentValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadEngagementsByEmployeeUuid.update_forward_refs()
ReadEngagementsByEmployeeUuidEngagements.update_forward_refs()
ReadEngagementsByEmployeeUuidEngagementsObjects.update_forward_refs()
ReadEngagementsByEmployeeUuidEngagementsObjectsCurrent.update_forward_refs()
ReadEngagementsByEmployeeUuidEngagementsObjectsCurrentValidity.update_forward_refs()
