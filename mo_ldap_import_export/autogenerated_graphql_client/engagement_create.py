from uuid import UUID

from .base_model import BaseModel


class EngagementCreate(BaseModel):
    engagement_create: "EngagementCreateEngagementCreate"


class EngagementCreateEngagementCreate(BaseModel):
    uuid: UUID


EngagementCreate.update_forward_refs()
EngagementCreateEngagementCreate.update_forward_refs()
