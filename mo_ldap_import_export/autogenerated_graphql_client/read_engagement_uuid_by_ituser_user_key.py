from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEngagementUuidByItuserUserKey(BaseModel):
    itusers: "ReadEngagementUuidByItuserUserKeyItusers"


class ReadEngagementUuidByItuserUserKeyItusers(BaseModel):
    objects: List["ReadEngagementUuidByItuserUserKeyItusersObjects"]


class ReadEngagementUuidByItuserUserKeyItusersObjects(BaseModel):
    current: Optional["ReadEngagementUuidByItuserUserKeyItusersObjectsCurrent"]


class ReadEngagementUuidByItuserUserKeyItusersObjectsCurrent(BaseModel):
    engagement_uuid: Optional[UUID]


ReadEngagementUuidByItuserUserKey.update_forward_refs()
ReadEngagementUuidByItuserUserKeyItusers.update_forward_refs()
ReadEngagementUuidByItuserUserKeyItusersObjects.update_forward_refs()
ReadEngagementUuidByItuserUserKeyItusersObjectsCurrent.update_forward_refs()
