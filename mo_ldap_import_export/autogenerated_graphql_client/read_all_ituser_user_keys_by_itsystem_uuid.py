from .base_model import BaseModel


class ReadAllItuserUserKeysByItsystemUuid(BaseModel):
    itusers: "ReadAllItuserUserKeysByItsystemUuidItusers"


class ReadAllItuserUserKeysByItsystemUuidItusers(BaseModel):
    objects: list["ReadAllItuserUserKeysByItsystemUuidItusersObjects"]


class ReadAllItuserUserKeysByItsystemUuidItusersObjects(BaseModel):
    validities: list["ReadAllItuserUserKeysByItsystemUuidItusersObjectsValidities"]


class ReadAllItuserUserKeysByItsystemUuidItusersObjectsValidities(BaseModel):
    user_key: str


ReadAllItuserUserKeysByItsystemUuid.update_forward_refs()
ReadAllItuserUserKeysByItsystemUuidItusers.update_forward_refs()
ReadAllItuserUserKeysByItsystemUuidItusersObjects.update_forward_refs()
ReadAllItuserUserKeysByItsystemUuidItusersObjectsValidities.update_forward_refs()
