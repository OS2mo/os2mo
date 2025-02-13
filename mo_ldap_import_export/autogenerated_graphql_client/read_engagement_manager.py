from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEngagementManager(BaseModel):
    engagements: "ReadEngagementManagerEngagements"


class ReadEngagementManagerEngagements(BaseModel):
    objects: list["ReadEngagementManagerEngagementsObjects"]


class ReadEngagementManagerEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementManagerEngagementsObjectsCurrent"]


class ReadEngagementManagerEngagementsObjectsCurrent(BaseModel):
    managers: list["ReadEngagementManagerEngagementsObjectsCurrentManagers"]


class ReadEngagementManagerEngagementsObjectsCurrentManagers(BaseModel):
    person: list["ReadEngagementManagerEngagementsObjectsCurrentManagersPerson"] | None


class ReadEngagementManagerEngagementsObjectsCurrentManagersPerson(BaseModel):
    uuid: UUID


ReadEngagementManager.update_forward_refs()
ReadEngagementManagerEngagements.update_forward_refs()
ReadEngagementManagerEngagementsObjects.update_forward_refs()
ReadEngagementManagerEngagementsObjectsCurrent.update_forward_refs()
ReadEngagementManagerEngagementsObjectsCurrentManagers.update_forward_refs()
ReadEngagementManagerEngagementsObjectsCurrentManagersPerson.update_forward_refs()
