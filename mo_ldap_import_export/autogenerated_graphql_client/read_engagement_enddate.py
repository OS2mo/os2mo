from datetime import datetime

from pydantic import Field

from .base_model import BaseModel


class ReadEngagementEnddate(BaseModel):
    engagements: "ReadEngagementEnddateEngagements"


class ReadEngagementEnddateEngagements(BaseModel):
    objects: list["ReadEngagementEnddateEngagementsObjects"]


class ReadEngagementEnddateEngagementsObjects(BaseModel):
    validities: list["ReadEngagementEnddateEngagementsObjectsValidities"]


class ReadEngagementEnddateEngagementsObjectsValidities(BaseModel):
    validity: "ReadEngagementEnddateEngagementsObjectsValiditiesValidity"


class ReadEngagementEnddateEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


ReadEngagementEnddate.update_forward_refs()
ReadEngagementEnddateEngagements.update_forward_refs()
ReadEngagementEnddateEngagementsObjects.update_forward_refs()
ReadEngagementEnddateEngagementsObjectsValidities.update_forward_refs()
ReadEngagementEnddateEngagementsObjectsValiditiesValidity.update_forward_refs()
