from uuid import UUID

from .base_model import BaseModel


class OrgUnitCreate(BaseModel):
    org_unit_create: "OrgUnitCreateOrgUnitCreate"


class OrgUnitCreateOrgUnitCreate(BaseModel):
    uuid: UUID


OrgUnitCreate.update_forward_refs()
OrgUnitCreateOrgUnitCreate.update_forward_refs()
