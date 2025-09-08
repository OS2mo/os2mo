from uuid import UUID

from .base_model import BaseModel


class GetEventNamespaces(BaseModel):
    event_namespaces: "GetEventNamespacesEventNamespaces"


class GetEventNamespacesEventNamespaces(BaseModel):
    objects: list["GetEventNamespacesEventNamespacesObjects"]


class GetEventNamespacesEventNamespacesObjects(BaseModel):
    name: str
    owner: UUID
    public: bool
    listeners: list["GetEventNamespacesEventNamespacesObjectsListeners"]


class GetEventNamespacesEventNamespacesObjectsListeners(BaseModel):
    owner: UUID
    routing_key: str
    user_key: str
    uuid: UUID


GetEventNamespaces.update_forward_refs()
GetEventNamespacesEventNamespaces.update_forward_refs()
GetEventNamespacesEventNamespacesObjects.update_forward_refs()
GetEventNamespacesEventNamespacesObjectsListeners.update_forward_refs()
