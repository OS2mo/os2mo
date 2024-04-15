from datetime import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagements(BaseModel):
    engagements: "ReadEngagementsEngagements"


class ReadEngagementsEngagements(BaseModel):
    objects: List["ReadEngagementsEngagementsObjects"]


class ReadEngagementsEngagementsObjects(BaseModel):
    validities: List["ReadEngagementsEngagementsObjectsValidities"]


class ReadEngagementsEngagementsObjectsValidities(BaseModel):
    user_key: str
    extension_1: Optional[str]
    extension_2: Optional[str]
    extension_3: Optional[str]
    extension_4: Optional[str]
    extension_5: Optional[str]
    extension_6: Optional[str]
    extension_7: Optional[str]
    extension_8: Optional[str]
    extension_9: Optional[str]
    extension_10: Optional[str]
    leave_uuid: Optional[UUID]
    primary_uuid: Optional[UUID]
    job_function_uuid: UUID
    org_unit_uuid: UUID
    engagement_type_uuid: UUID
    employee_uuid: UUID
    validity: "ReadEngagementsEngagementsObjectsValiditiesValidity"


class ReadEngagementsEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


ReadEngagements.update_forward_refs()
ReadEngagementsEngagements.update_forward_refs()
ReadEngagementsEngagementsObjects.update_forward_refs()
ReadEngagementsEngagementsObjectsValidities.update_forward_refs()
ReadEngagementsEngagementsObjectsValiditiesValidity.update_forward_refs()
