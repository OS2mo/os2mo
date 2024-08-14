from uuid import UUID

from .base_model import BaseModel


class TestingOrgUnitCreate(BaseModel):
    org_unit_create: "TestingOrgUnitCreateOrgUnitCreate"


class TestingOrgUnitCreateOrgUnitCreate(BaseModel):
    uuid: UUID


TestingOrgUnitCreate.update_forward_refs()
TestingOrgUnitCreateOrgUnitCreate.update_forward_refs()
