from uuid import UUID

from .base_model import BaseModel


class CreateItSystem(BaseModel):
    itsystem_create: "CreateItSystemItsystemCreate"


class CreateItSystemItsystemCreate(BaseModel):
    uuid: UUID


CreateItSystem.update_forward_refs()
CreateItSystemItsystemCreate.update_forward_refs()
