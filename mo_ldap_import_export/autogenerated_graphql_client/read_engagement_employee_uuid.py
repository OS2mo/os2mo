from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEngagementEmployeeUuid(BaseModel):
    engagements: "ReadEngagementEmployeeUuidEngagements"


class ReadEngagementEmployeeUuidEngagements(BaseModel):
    objects: List["ReadEngagementEmployeeUuidEngagementsObjects"]


class ReadEngagementEmployeeUuidEngagementsObjects(BaseModel):
    current: Optional["ReadEngagementEmployeeUuidEngagementsObjectsCurrent"]


class ReadEngagementEmployeeUuidEngagementsObjectsCurrent(BaseModel):
    employee_uuid: UUID


ReadEngagementEmployeeUuid.update_forward_refs()
ReadEngagementEmployeeUuidEngagements.update_forward_refs()
ReadEngagementEmployeeUuidEngagementsObjects.update_forward_refs()
ReadEngagementEmployeeUuidEngagementsObjectsCurrent.update_forward_refs()
