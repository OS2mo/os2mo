from uuid import UUID

from .base_model import BaseModel


class ClassTerminate(BaseModel):
    class_terminate: "ClassTerminateClassTerminate"


class ClassTerminateClassTerminate(BaseModel):
    uuid: UUID


ClassTerminate.update_forward_refs()
ClassTerminateClassTerminate.update_forward_refs()
