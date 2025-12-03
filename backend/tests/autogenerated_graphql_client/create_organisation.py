from uuid import UUID

from .base_model import BaseModel


class CreateOrganisation(BaseModel):
    org_create: "CreateOrganisationOrgCreate"


class CreateOrganisationOrgCreate(BaseModel):
    uuid: UUID


CreateOrganisation.update_forward_refs()
CreateOrganisationOrgCreate.update_forward_refs()
