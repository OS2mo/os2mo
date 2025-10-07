from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class Itusers(BaseModel):
    itusers: "ItusersItusers"


class ItusersItusers(BaseModel):
    objects: list["ItusersItusersObjects"]


class ItusersItusersObjects(BaseModel):
    uuid: UUID
    current: Optional["ItusersItusersObjectsCurrent"]


class ItusersItusersObjectsCurrent(BaseModel):
    external_id: str | None


Itusers.update_forward_refs()
ItusersItusers.update_forward_refs()
ItusersItusersObjects.update_forward_refs()
ItusersItusersObjectsCurrent.update_forward_refs()
