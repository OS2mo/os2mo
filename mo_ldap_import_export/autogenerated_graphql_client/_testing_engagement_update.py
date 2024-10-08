from uuid import UUID

from .base_model import BaseModel


class TestingEngagementUpdate(BaseModel):
    engagement_update: "TestingEngagementUpdateEngagementUpdate"


class TestingEngagementUpdateEngagementUpdate(BaseModel):
    uuid: UUID


TestingEngagementUpdate.update_forward_refs()
TestingEngagementUpdateEngagementUpdate.update_forward_refs()
