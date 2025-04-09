from uuid import UUID

from .base_model import BaseModel


class ItsystemTerminate(BaseModel):
    itsystem_terminate: "ItsystemTerminateItsystemTerminate"


class ItsystemTerminateItsystemTerminate(BaseModel):
    uuid: UUID


ItsystemTerminate.update_forward_refs()
ItsystemTerminateItsystemTerminate.update_forward_refs()
