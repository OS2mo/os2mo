from uuid import UUID

from .base_model import BaseModel


class ReadEventListeners(BaseModel):
    event_listeners: "ReadEventListenersEventListeners"


class ReadEventListenersEventListeners(BaseModel):
    objects: list["ReadEventListenersEventListenersObjects"]


class ReadEventListenersEventListenersObjects(BaseModel):
    uuid: UUID
    user_key: str
    routing_key: str


ReadEventListeners.update_forward_refs()
ReadEventListenersEventListeners.update_forward_refs()
ReadEventListenersEventListenersObjects.update_forward_refs()
