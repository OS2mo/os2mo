from uuid import UUID

from .base_model import BaseModel


class TestingEngagementTerminate(BaseModel):
    engagement_terminate: "TestingEngagementTerminateEngagementTerminate"


class TestingEngagementTerminateEngagementTerminate(BaseModel):
    uuid: UUID


TestingEngagementTerminate.update_forward_refs()
TestingEngagementTerminateEngagementTerminate.update_forward_refs()
