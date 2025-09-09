from .base_model import BaseModel


class ListEvents(BaseModel):
    events: "ListEventsEvents"


class ListEventsEvents(BaseModel):
    objects: list["ListEventsEventsObjects"]


class ListEventsEventsObjects(BaseModel):
    subject: str


ListEvents.update_forward_refs()
ListEventsEvents.update_forward_refs()
ListEventsEventsObjects.update_forward_refs()
