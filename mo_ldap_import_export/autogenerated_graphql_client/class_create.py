from uuid import UUID

from .base_model import BaseModel


class ClassCreate(BaseModel):
    class_create: "ClassCreateClassCreate"


class ClassCreateClassCreate(BaseModel):
    uuid: UUID


ClassCreate.update_forward_refs()
ClassCreateClassCreate.update_forward_refs()
