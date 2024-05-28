from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagementsIsPrimary(BaseModel):
    engagements: "ReadEngagementsIsPrimaryEngagements"


class ReadEngagementsIsPrimaryEngagements(BaseModel):
    objects: List["ReadEngagementsIsPrimaryEngagementsObjects"]


class ReadEngagementsIsPrimaryEngagementsObjects(BaseModel):
    validities: List["ReadEngagementsIsPrimaryEngagementsObjectsValidities"]


class ReadEngagementsIsPrimaryEngagementsObjectsValidities(BaseModel):
    is_primary: bool
    uuid: UUID
    validity: "ReadEngagementsIsPrimaryEngagementsObjectsValiditiesValidity"


class ReadEngagementsIsPrimaryEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


ReadEngagementsIsPrimary.update_forward_refs()
ReadEngagementsIsPrimaryEngagements.update_forward_refs()
ReadEngagementsIsPrimaryEngagementsObjects.update_forward_refs()
ReadEngagementsIsPrimaryEngagementsObjectsValidities.update_forward_refs()
ReadEngagementsIsPrimaryEngagementsObjectsValiditiesValidity.update_forward_refs()
