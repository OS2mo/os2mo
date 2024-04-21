from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadAllAddressesUuids(BaseModel):
    addresses: "ReadAllAddressesUuidsAddresses"


class ReadAllAddressesUuidsAddresses(BaseModel):
    objects: List["ReadAllAddressesUuidsAddressesObjects"]
    page_info: "ReadAllAddressesUuidsAddressesPageInfo"


class ReadAllAddressesUuidsAddressesObjects(BaseModel):
    validities: List["ReadAllAddressesUuidsAddressesObjectsValidities"]


class ReadAllAddressesUuidsAddressesObjectsValidities(BaseModel):
    uuid: UUID
    org_unit_uuid: Optional[UUID]
    employee_uuid: Optional[UUID]
    validity: "ReadAllAddressesUuidsAddressesObjectsValiditiesValidity"


class ReadAllAddressesUuidsAddressesObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class ReadAllAddressesUuidsAddressesPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllAddressesUuids.update_forward_refs()
ReadAllAddressesUuidsAddresses.update_forward_refs()
ReadAllAddressesUuidsAddressesObjects.update_forward_refs()
ReadAllAddressesUuidsAddressesObjectsValidities.update_forward_refs()
ReadAllAddressesUuidsAddressesObjectsValiditiesValidity.update_forward_refs()
ReadAllAddressesUuidsAddressesPageInfo.update_forward_refs()
