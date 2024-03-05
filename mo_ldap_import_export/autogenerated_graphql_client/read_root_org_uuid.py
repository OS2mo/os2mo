from uuid import UUID

from .base_model import BaseModel


class ReadRootOrgUuid(BaseModel):
    org: "ReadRootOrgUuidOrg"


class ReadRootOrgUuidOrg(BaseModel):
    uuid: UUID


ReadRootOrgUuid.update_forward_refs()
ReadRootOrgUuidOrg.update_forward_refs()
