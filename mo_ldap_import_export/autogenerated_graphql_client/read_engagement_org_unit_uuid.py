from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEngagementOrgUnitUuid(BaseModel):
    engagements: "ReadEngagementOrgUnitUuidEngagements"


class ReadEngagementOrgUnitUuidEngagements(BaseModel):
    objects: List["ReadEngagementOrgUnitUuidEngagementsObjects"]


class ReadEngagementOrgUnitUuidEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementOrgUnitUuidEngagementsObjectsCurrent"]


class ReadEngagementOrgUnitUuidEngagementsObjectsCurrent(BaseModel):
    org_unit_uuid: UUID


ReadEngagementOrgUnitUuid.update_forward_refs()
ReadEngagementOrgUnitUuidEngagements.update_forward_refs()
ReadEngagementOrgUnitUuidEngagementsObjects.update_forward_refs()
ReadEngagementOrgUnitUuidEngagementsObjectsCurrent.update_forward_refs()
