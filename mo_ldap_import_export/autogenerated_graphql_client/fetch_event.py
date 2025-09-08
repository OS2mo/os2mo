from typing import Any
from typing import Optional

from .base_model import BaseModel


class FetchEvent(BaseModel):
    event_fetch: Optional["FetchEventEventFetch"]


class FetchEventEventFetch(BaseModel):
    token: Any
    subject: str


FetchEvent.update_forward_refs()
FetchEventEventFetch.update_forward_refs()
