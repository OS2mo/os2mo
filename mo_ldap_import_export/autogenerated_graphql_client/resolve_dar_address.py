from typing import Literal
from typing import Optional
from typing import Union
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ResolveDarAddress(BaseModel):
    addresses: "ResolveDarAddressAddresses"


class ResolveDarAddressAddresses(BaseModel):
    objects: list["ResolveDarAddressAddressesObjects"]


class ResolveDarAddressAddressesObjects(BaseModel):
    uuid: UUID
    current: Optional["ResolveDarAddressAddressesObjectsCurrent"]


class ResolveDarAddressAddressesObjectsCurrent(BaseModel):
    resolve: Union[
        "ResolveDarAddressAddressesObjectsCurrentResolveResolvedAddress",
        "ResolveDarAddressAddressesObjectsCurrentResolveDARAddress",
    ] = Field(discriminator="typename__")


class ResolveDarAddressAddressesObjectsCurrentResolveResolvedAddress(BaseModel):
    typename__: Literal["DefaultAddress", "MultifieldAddress", "ResolvedAddress"] = (
        Field(alias="__typename")
    )
    value: str


class ResolveDarAddressAddressesObjectsCurrentResolveDARAddress(BaseModel):
    typename__: Literal["DARAddress"] = Field(alias="__typename")
    zip_code: str
    zip_code_name: str
    road_name: str
    value: str


ResolveDarAddress.update_forward_refs()
ResolveDarAddressAddresses.update_forward_refs()
ResolveDarAddressAddressesObjects.update_forward_refs()
ResolveDarAddressAddressesObjectsCurrent.update_forward_refs()
ResolveDarAddressAddressesObjectsCurrentResolveResolvedAddress.update_forward_refs()
ResolveDarAddressAddressesObjectsCurrentResolveDARAddress.update_forward_refs()
