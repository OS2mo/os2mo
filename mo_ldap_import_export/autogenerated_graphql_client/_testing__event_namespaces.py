from uuid import UUID

from .base_model import BaseModel


class TestingEventNamespaces(BaseModel):
    event_namespaces: "TestingEventNamespacesEventNamespaces"


class TestingEventNamespacesEventNamespaces(BaseModel):
    objects: list["TestingEventNamespacesEventNamespacesObjects"]


class TestingEventNamespacesEventNamespacesObjects(BaseModel):
    name: str
    owner: UUID
    public: bool
    listeners: list["TestingEventNamespacesEventNamespacesObjectsListeners"]


class TestingEventNamespacesEventNamespacesObjectsListeners(BaseModel):
    owner: UUID
    routing_key: str
    user_key: str
    uuid: UUID


TestingEventNamespaces.update_forward_refs()
TestingEventNamespacesEventNamespaces.update_forward_refs()
TestingEventNamespacesEventNamespacesObjects.update_forward_refs()
TestingEventNamespacesEventNamespacesObjectsListeners.update_forward_refs()
