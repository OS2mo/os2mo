from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEngagementsByEngagementsFilter(BaseModel):
    engagements: "ReadEngagementsByEngagementsFilterEngagements"


class ReadEngagementsByEngagementsFilterEngagements(BaseModel):
    objects: List["ReadEngagementsByEngagementsFilterEngagementsObjects"]


class ReadEngagementsByEngagementsFilterEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementsByEngagementsFilterEngagementsObjectsCurrent"]


class ReadEngagementsByEngagementsFilterEngagementsObjectsCurrent(BaseModel):
    uuid: UUID
    user_key: str
    org_unit_uuid: UUID
    job_function_uuid: UUID
    engagement_type_uuid: UUID
    primary_uuid: Optional[UUID]


ReadEngagementsByEngagementsFilter.update_forward_refs()
ReadEngagementsByEngagementsFilterEngagements.update_forward_refs()
ReadEngagementsByEngagementsFilterEngagementsObjects.update_forward_refs()
ReadEngagementsByEngagementsFilterEngagementsObjectsCurrent.update_forward_refs()
