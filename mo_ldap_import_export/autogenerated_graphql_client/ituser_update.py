from uuid import UUID

from .base_model import BaseModel


class ItuserUpdate(BaseModel):
    ituser_update: "ItuserUpdateItuserUpdate"


class ItuserUpdateItuserUpdate(BaseModel):
    uuid: UUID


ItuserUpdate.update_forward_refs()
ItuserUpdateItuserUpdate.update_forward_refs()
