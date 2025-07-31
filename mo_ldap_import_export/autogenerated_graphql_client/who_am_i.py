from uuid import UUID

from .base_model import BaseModel


class WhoAmI(BaseModel):
    me: "WhoAmIMe"


class WhoAmIMe(BaseModel):
    actor: "WhoAmIMeActor"


class WhoAmIMeActor(BaseModel):
    uuid: UUID


WhoAmI.update_forward_refs()
WhoAmIMe.update_forward_refs()
WhoAmIMeActor.update_forward_refs()
