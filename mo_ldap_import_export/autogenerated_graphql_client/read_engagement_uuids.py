from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagementUuids(BaseModel):
    engagements: "ReadEngagementUuidsEngagements"


class ReadEngagementUuidsEngagements(BaseModel):
    objects: list["ReadEngagementUuidsEngagementsObjects"]


class ReadEngagementUuidsEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementUuidsEngagementsObjectsCurrent"]


class ReadEngagementUuidsEngagementsObjectsCurrent(BaseModel):
    uuid: UUID
    validity: "ReadEngagementUuidsEngagementsObjectsCurrentValidity"


class ReadEngagementUuidsEngagementsObjectsCurrentValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadEngagementUuids.update_forward_refs()
ReadEngagementUuidsEngagements.update_forward_refs()
ReadEngagementUuidsEngagementsObjects.update_forward_refs()
ReadEngagementUuidsEngagementsObjectsCurrent.update_forward_refs()
ReadEngagementUuidsEngagementsObjectsCurrentValidity.update_forward_refs()
