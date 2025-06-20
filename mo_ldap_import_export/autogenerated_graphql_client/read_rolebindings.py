from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadRolebindings(BaseModel):
    rolebindings: "ReadRolebindingsRolebindings"


class ReadRolebindingsRolebindings(BaseModel):
    objects: list["ReadRolebindingsRolebindingsObjects"]


class ReadRolebindingsRolebindingsObjects(BaseModel):
    current: Optional["ReadRolebindingsRolebindingsObjectsCurrent"]


class ReadRolebindingsRolebindingsObjectsCurrent(BaseModel):
    ituser: list["ReadRolebindingsRolebindingsObjectsCurrentItuser"]


class ReadRolebindingsRolebindingsObjectsCurrentItuser(BaseModel):
    person: list["ReadRolebindingsRolebindingsObjectsCurrentItuserPerson"] | None


class ReadRolebindingsRolebindingsObjectsCurrentItuserPerson(BaseModel):
    uuid: UUID


ReadRolebindings.update_forward_refs()
ReadRolebindingsRolebindings.update_forward_refs()
ReadRolebindingsRolebindingsObjects.update_forward_refs()
ReadRolebindingsRolebindingsObjectsCurrent.update_forward_refs()
ReadRolebindingsRolebindingsObjectsCurrentItuser.update_forward_refs()
ReadRolebindingsRolebindingsObjectsCurrentItuserPerson.update_forward_refs()
