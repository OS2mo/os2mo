from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class TestingAddressRead(BaseModel):
    addresses: "TestingAddressReadAddresses"


class TestingAddressReadAddresses(BaseModel):
    objects: list["TestingAddressReadAddressesObjects"]


class TestingAddressReadAddressesObjects(BaseModel):
    validities: list["TestingAddressReadAddressesObjectsValidities"]


class TestingAddressReadAddressesObjectsValidities(BaseModel):
    uuid: UUID
    user_key: str
    address_type: "TestingAddressReadAddressesObjectsValiditiesAddressType"
    value: str
    value2: str | None
    person: list["TestingAddressReadAddressesObjectsValiditiesPerson"] | None
    visibility: Optional["TestingAddressReadAddressesObjectsValiditiesVisibility"]
    validity: "TestingAddressReadAddressesObjectsValiditiesValidity"


class TestingAddressReadAddressesObjectsValiditiesAddressType(BaseModel):
    user_key: str


class TestingAddressReadAddressesObjectsValiditiesPerson(BaseModel):
    uuid: UUID


class TestingAddressReadAddressesObjectsValiditiesVisibility(BaseModel):
    user_key: str


class TestingAddressReadAddressesObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None


TestingAddressRead.update_forward_refs()
TestingAddressReadAddresses.update_forward_refs()
TestingAddressReadAddressesObjects.update_forward_refs()
TestingAddressReadAddressesObjectsValidities.update_forward_refs()
TestingAddressReadAddressesObjectsValiditiesAddressType.update_forward_refs()
TestingAddressReadAddressesObjectsValiditiesPerson.update_forward_refs()
TestingAddressReadAddressesObjectsValiditiesVisibility.update_forward_refs()
TestingAddressReadAddressesObjectsValiditiesValidity.update_forward_refs()
