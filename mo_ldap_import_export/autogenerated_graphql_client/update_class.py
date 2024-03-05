from uuid import UUID

from .base_model import BaseModel


class UpdateClass(BaseModel):
    class_update: "UpdateClassClassUpdate"


class UpdateClassClassUpdate(BaseModel):
    uuid: UUID


UpdateClass.update_forward_refs()
UpdateClassClassUpdate.update_forward_refs()
