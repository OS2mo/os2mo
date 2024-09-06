from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadEmployeesWithEngagementToOrgUnit(BaseModel):
    engagements: "ReadEmployeesWithEngagementToOrgUnitEngagements"


class ReadEmployeesWithEngagementToOrgUnitEngagements(BaseModel):
    objects: list["ReadEmployeesWithEngagementToOrgUnitEngagementsObjects"]


class ReadEmployeesWithEngagementToOrgUnitEngagementsObjects(BaseModel):
    current: Optional["ReadEmployeesWithEngagementToOrgUnitEngagementsObjectsCurrent"]


class ReadEmployeesWithEngagementToOrgUnitEngagementsObjectsCurrent(BaseModel):
    employee_uuid: UUID


ReadEmployeesWithEngagementToOrgUnit.update_forward_refs()
ReadEmployeesWithEngagementToOrgUnitEngagements.update_forward_refs()
ReadEmployeesWithEngagementToOrgUnitEngagementsObjects.update_forward_refs()
ReadEmployeesWithEngagementToOrgUnitEngagementsObjectsCurrent.update_forward_refs()
