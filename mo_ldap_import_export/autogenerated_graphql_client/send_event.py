from .base_model import BaseModel


class SendEvent(BaseModel):
    event_send: bool


SendEvent.update_forward_refs()
