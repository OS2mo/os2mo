from uuid import UUID

from .base_model import BaseModel


class EngagementUpdate(BaseModel):
    engagement_update: "EngagementUpdateEngagementUpdate"


class EngagementUpdateEngagementUpdate(BaseModel):
    uuid: UUID


EngagementUpdate.update_forward_refs()
EngagementUpdateEngagementUpdate.update_forward_refs()
