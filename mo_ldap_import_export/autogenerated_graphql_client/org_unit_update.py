from uuid import UUID

from .base_model import BaseModel


class OrgUnitUpdate(BaseModel):
    org_unit_update: "OrgUnitUpdateOrgUnitUpdate"


class OrgUnitUpdateOrgUnitUpdate(BaseModel):
    uuid: UUID


OrgUnitUpdate.update_forward_refs()
OrgUnitUpdateOrgUnitUpdate.update_forward_refs()
