from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagementUuids(BaseModel):
    engagements: "ReadEngagementUuidsEngagements"


class ReadEngagementUuidsEngagements(BaseModel):
    objects: list["ReadEngagementUuidsEngagementsObjects"]


class ReadEngagementUuidsEngagementsObjects(BaseModel):
    validities: list["ReadEngagementUuidsEngagementsObjectsValidities"]


class ReadEngagementUuidsEngagementsObjectsValidities(BaseModel):
    uuid: UUID
    validity: "ReadEngagementUuidsEngagementsObjectsValiditiesValidity"


class ReadEngagementUuidsEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadEngagementUuids.update_forward_refs()
ReadEngagementUuidsEngagements.update_forward_refs()
ReadEngagementUuidsEngagementsObjects.update_forward_refs()
ReadEngagementUuidsEngagementsObjectsValidities.update_forward_refs()
ReadEngagementUuidsEngagementsObjectsValiditiesValidity.update_forward_refs()
