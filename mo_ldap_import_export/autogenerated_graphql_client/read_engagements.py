from datetime import datetime
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadEngagements(BaseModel):
    engagements: "ReadEngagementsEngagements"


class ReadEngagementsEngagements(BaseModel):
    objects: list["ReadEngagementsEngagementsObjects"]


class ReadEngagementsEngagementsObjects(BaseModel):
    validities: list["ReadEngagementsEngagementsObjectsValidities"]


class ReadEngagementsEngagementsObjectsValidities(BaseModel):
    user_key: str
    extension_1: str | None
    extension_2: str | None
    extension_3: str | None
    extension_4: str | None
    extension_5: str | None
    extension_6: str | None
    extension_7: str | None
    extension_8: str | None
    extension_9: str | None
    extension_10: str | None
    fraction: int | None
    leave_uuid: UUID | None
    primary_uuid: UUID | None
    job_function_uuid: UUID
    org_unit_uuid: UUID
    engagement_type_uuid: UUID
    employee_uuid: UUID
    validity: "ReadEngagementsEngagementsObjectsValiditiesValidity"


class ReadEngagementsEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadEngagements.update_forward_refs()
ReadEngagementsEngagements.update_forward_refs()
ReadEngagementsEngagementsObjects.update_forward_refs()
ReadEngagementsEngagementsObjectsValidities.update_forward_refs()
ReadEngagementsEngagementsObjectsValiditiesValidity.update_forward_refs()
