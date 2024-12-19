from uuid import UUID

from .base_model import BaseModel


class ReadEngagementUuid(BaseModel):
    engagements: "ReadEngagementUuidEngagements"


class ReadEngagementUuidEngagements(BaseModel):
    objects: list["ReadEngagementUuidEngagementsObjects"]


class ReadEngagementUuidEngagementsObjects(BaseModel):
    uuid: UUID


ReadEngagementUuid.update_forward_refs()
ReadEngagementUuidEngagements.update_forward_refs()
ReadEngagementUuidEngagementsObjects.update_forward_refs()
