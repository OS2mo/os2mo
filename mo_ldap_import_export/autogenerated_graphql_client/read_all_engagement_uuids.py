from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadAllEngagementUuids(BaseModel):
    engagements: "ReadAllEngagementUuidsEngagements"


class ReadAllEngagementUuidsEngagements(BaseModel):
    objects: List["ReadAllEngagementUuidsEngagementsObjects"]
    page_info: "ReadAllEngagementUuidsEngagementsPageInfo"


class ReadAllEngagementUuidsEngagementsObjects(BaseModel):
    validities: List["ReadAllEngagementUuidsEngagementsObjectsValidities"]


class ReadAllEngagementUuidsEngagementsObjectsValidities(BaseModel):
    uuid: UUID
    org_unit_uuid: UUID
    employee_uuid: UUID
    validity: "ReadAllEngagementUuidsEngagementsObjectsValiditiesValidity"


class ReadAllEngagementUuidsEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class ReadAllEngagementUuidsEngagementsPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllEngagementUuids.update_forward_refs()
ReadAllEngagementUuidsEngagements.update_forward_refs()
ReadAllEngagementUuidsEngagementsObjects.update_forward_refs()
ReadAllEngagementUuidsEngagementsObjectsValidities.update_forward_refs()
ReadAllEngagementUuidsEngagementsObjectsValiditiesValidity.update_forward_refs()
ReadAllEngagementUuidsEngagementsPageInfo.update_forward_refs()
