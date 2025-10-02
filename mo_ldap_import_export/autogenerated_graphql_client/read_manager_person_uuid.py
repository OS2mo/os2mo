from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadManagerPersonUuid(BaseModel):
    managers: "ReadManagerPersonUuidManagers"


class ReadManagerPersonUuidManagers(BaseModel):
    objects: list["ReadManagerPersonUuidManagersObjects"]


class ReadManagerPersonUuidManagersObjects(BaseModel):
    current: Optional["ReadManagerPersonUuidManagersObjectsCurrent"]


class ReadManagerPersonUuidManagersObjectsCurrent(BaseModel):
    person: list["ReadManagerPersonUuidManagersObjectsCurrentPerson"] | None


class ReadManagerPersonUuidManagersObjectsCurrentPerson(BaseModel):
    uuid: UUID


ReadManagerPersonUuid.update_forward_refs()
ReadManagerPersonUuidManagers.update_forward_refs()
ReadManagerPersonUuidManagersObjects.update_forward_refs()
ReadManagerPersonUuidManagersObjectsCurrent.update_forward_refs()
ReadManagerPersonUuidManagersObjectsCurrentPerson.update_forward_refs()
