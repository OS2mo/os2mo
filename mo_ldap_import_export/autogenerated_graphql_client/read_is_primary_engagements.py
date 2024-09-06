from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadIsPrimaryEngagements(BaseModel):
    engagements: "ReadIsPrimaryEngagementsEngagements"


class ReadIsPrimaryEngagementsEngagements(BaseModel):
    objects: list["ReadIsPrimaryEngagementsEngagementsObjects"]


class ReadIsPrimaryEngagementsEngagementsObjects(BaseModel):
    current: Optional["ReadIsPrimaryEngagementsEngagementsObjectsCurrent"]


class ReadIsPrimaryEngagementsEngagementsObjectsCurrent(BaseModel):
    is_primary: bool
    uuid: UUID


ReadIsPrimaryEngagements.update_forward_refs()
ReadIsPrimaryEngagementsEngagements.update_forward_refs()
ReadIsPrimaryEngagementsEngagementsObjects.update_forward_refs()
ReadIsPrimaryEngagementsEngagementsObjectsCurrent.update_forward_refs()
