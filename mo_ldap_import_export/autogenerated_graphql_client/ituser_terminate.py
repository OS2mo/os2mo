from uuid import UUID

from .base_model import BaseModel


class ItuserTerminate(BaseModel):
    ituser_terminate: "ItuserTerminateItuserTerminate"


class ItuserTerminateItuserTerminate(BaseModel):
    uuid: UUID


ItuserTerminate.update_forward_refs()
ItuserTerminateItuserTerminate.update_forward_refs()
