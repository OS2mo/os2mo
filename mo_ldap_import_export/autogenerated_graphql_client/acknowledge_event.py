from .base_model import BaseModel


class AcknowledgeEvent(BaseModel):
    event_acknowledge: bool


AcknowledgeEvent.update_forward_refs()
