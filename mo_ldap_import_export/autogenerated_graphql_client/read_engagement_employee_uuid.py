from uuid import UUID

from .base_model import BaseModel


class ReadEngagementEmployeeUuid(BaseModel):
    engagements: "ReadEngagementEmployeeUuidEngagements"


class ReadEngagementEmployeeUuidEngagements(BaseModel):
    objects: list["ReadEngagementEmployeeUuidEngagementsObjects"]


class ReadEngagementEmployeeUuidEngagementsObjects(BaseModel):
    validities: list["ReadEngagementEmployeeUuidEngagementsObjectsValidities"]


class ReadEngagementEmployeeUuidEngagementsObjectsValidities(BaseModel):
    employee_uuid: UUID


ReadEngagementEmployeeUuid.update_forward_refs()
ReadEngagementEmployeeUuidEngagements.update_forward_refs()
ReadEngagementEmployeeUuidEngagementsObjects.update_forward_refs()
ReadEngagementEmployeeUuidEngagementsObjectsValidities.update_forward_refs()
