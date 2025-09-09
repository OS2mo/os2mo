from uuid import UUID

from .base_model import BaseModel


class DeclareEventListener(BaseModel):
    event_listener_declare: "DeclareEventListenerEventListenerDeclare"


class DeclareEventListenerEventListenerDeclare(BaseModel):
    uuid: UUID


DeclareEventListener.update_forward_refs()
DeclareEventListenerEventListenerDeclare.update_forward_refs()
