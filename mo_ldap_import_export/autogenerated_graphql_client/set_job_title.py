from uuid import UUID

from .base_model import BaseModel


class SetJobTitle(BaseModel):
    engagement_update: "SetJobTitleEngagementUpdate"


class SetJobTitleEngagementUpdate(BaseModel):
    uuid: UUID


SetJobTitle.update_forward_refs()
SetJobTitleEngagementUpdate.update_forward_refs()
