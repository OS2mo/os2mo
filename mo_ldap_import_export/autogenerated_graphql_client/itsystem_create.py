from uuid import UUID

from .base_model import BaseModel


class ItsystemCreate(BaseModel):
    itsystem_create: "ItsystemCreateItsystemCreate"


class ItsystemCreateItsystemCreate(BaseModel):
    uuid: UUID


ItsystemCreate.update_forward_refs()
ItsystemCreateItsystemCreate.update_forward_refs()
