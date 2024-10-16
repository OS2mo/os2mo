from uuid import UUID

from .base_model import BaseModel


class ItuserCreate(BaseModel):
    ituser_create: "ItuserCreateItuserCreate"


class ItuserCreateItuserCreate(BaseModel):
    uuid: UUID


ItuserCreate.update_forward_refs()
ItuserCreateItuserCreate.update_forward_refs()
