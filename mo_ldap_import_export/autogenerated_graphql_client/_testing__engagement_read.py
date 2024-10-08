from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class TestingEngagementRead(BaseModel):
    engagements: "TestingEngagementReadEngagements"


class TestingEngagementReadEngagements(BaseModel):
    objects: list["TestingEngagementReadEngagementsObjects"]


class TestingEngagementReadEngagementsObjects(BaseModel):
    validities: list["TestingEngagementReadEngagementsObjectsValidities"]


class TestingEngagementReadEngagementsObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    person: list["TestingEngagementReadEngagementsObjectsValiditiesPerson"]
    org_unit: list["TestingEngagementReadEngagementsObjectsValiditiesOrgUnit"]
    engagement_type: "TestingEngagementReadEngagementsObjectsValiditiesEngagementType"
    job_function: "TestingEngagementReadEngagementsObjectsValiditiesJobFunction"
    primary: Optional["TestingEngagementReadEngagementsObjectsValiditiesPrimary"]
    extension_1: str | None
    validity: "TestingEngagementReadEngagementsObjectsValiditiesValidity"


class TestingEngagementReadEngagementsObjectsValiditiesPerson(BaseModel):
    uuid: UUID


class TestingEngagementReadEngagementsObjectsValiditiesOrgUnit(BaseModel):
    uuid: UUID


class TestingEngagementReadEngagementsObjectsValiditiesEngagementType(BaseModel):
    user_key: str


class TestingEngagementReadEngagementsObjectsValiditiesJobFunction(BaseModel):
    user_key: str


class TestingEngagementReadEngagementsObjectsValiditiesPrimary(BaseModel):
    user_key: str


class TestingEngagementReadEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


TestingEngagementRead.update_forward_refs()
TestingEngagementReadEngagements.update_forward_refs()
TestingEngagementReadEngagementsObjects.update_forward_refs()
TestingEngagementReadEngagementsObjectsValidities.update_forward_refs()
TestingEngagementReadEngagementsObjectsValiditiesPerson.update_forward_refs()
TestingEngagementReadEngagementsObjectsValiditiesOrgUnit.update_forward_refs()
TestingEngagementReadEngagementsObjectsValiditiesEngagementType.update_forward_refs()
TestingEngagementReadEngagementsObjectsValiditiesJobFunction.update_forward_refs()
TestingEngagementReadEngagementsObjectsValiditiesPrimary.update_forward_refs()
TestingEngagementReadEngagementsObjectsValiditiesValidity.update_forward_refs()
