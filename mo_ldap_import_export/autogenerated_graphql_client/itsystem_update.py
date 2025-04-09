from uuid import UUID

from .base_model import BaseModel


class ItsystemUpdate(BaseModel):
    itsystem_update: "ItsystemUpdateItsystemUpdate"


class ItsystemUpdateItsystemUpdate(BaseModel):
    uuid: UUID


ItsystemUpdate.update_forward_refs()
ItsystemUpdateItsystemUpdate.update_forward_refs()
