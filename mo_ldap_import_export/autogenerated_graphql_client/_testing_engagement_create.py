from uuid import UUID

from .base_model import BaseModel


class TestingEngagementCreate(BaseModel):
    engagement_create: "TestingEngagementCreateEngagementCreate"


class TestingEngagementCreateEngagementCreate(BaseModel):
    uuid: UUID


TestingEngagementCreate.update_forward_refs()
TestingEngagementCreateEngagementCreate.update_forward_refs()
