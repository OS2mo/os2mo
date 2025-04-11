from uuid import UUID

from .base_model import BaseModel


class ClassUpdate(BaseModel):
    class_update: "ClassUpdateClassUpdate"


class ClassUpdateClassUpdate(BaseModel):
    uuid: UUID


ClassUpdate.update_forward_refs()
ClassUpdateClassUpdate.update_forward_refs()
