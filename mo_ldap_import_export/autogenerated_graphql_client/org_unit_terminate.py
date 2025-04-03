from uuid import UUID

from .base_model import BaseModel


class OrgUnitTerminate(BaseModel):
    org_unit_terminate: "OrgUnitTerminateOrgUnitTerminate"


class OrgUnitTerminateOrgUnitTerminate(BaseModel):
    uuid: UUID


OrgUnitTerminate.update_forward_refs()
OrgUnitTerminateOrgUnitTerminate.update_forward_refs()
