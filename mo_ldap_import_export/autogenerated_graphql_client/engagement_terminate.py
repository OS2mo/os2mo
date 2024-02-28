from uuid import UUID

from .base_model import BaseModel


class EngagementTerminate(BaseModel):
    engagement_terminate: "EngagementTerminateEngagementTerminate"


class EngagementTerminateEngagementTerminate(BaseModel):
    uuid: UUID


EngagementTerminate.update_forward_refs()
EngagementTerminateEngagementTerminate.update_forward_refs()
