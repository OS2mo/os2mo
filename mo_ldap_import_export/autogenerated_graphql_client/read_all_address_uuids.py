from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class ReadAllAddressUuids(BaseModel):
    addresses: "ReadAllAddressUuidsAddresses"


class ReadAllAddressUuidsAddresses(BaseModel):
    objects: List["ReadAllAddressUuidsAddressesObjects"]
    page_info: "ReadAllAddressUuidsAddressesPageInfo"


class ReadAllAddressUuidsAddressesObjects(BaseModel):
    validities: List["ReadAllAddressUuidsAddressesObjectsValidities"]


class ReadAllAddressUuidsAddressesObjectsValidities(BaseModel):
    uuid: UUID
    org_unit_uuid: Optional[UUID]
    employee_uuid: Optional[UUID]
    validity: "ReadAllAddressUuidsAddressesObjectsValiditiesValidity"


class ReadAllAddressUuidsAddressesObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class ReadAllAddressUuidsAddressesPageInfo(BaseModel):
    next_cursor: Optional[Any]


ReadAllAddressUuids.update_forward_refs()
ReadAllAddressUuidsAddresses.update_forward_refs()
ReadAllAddressUuidsAddressesObjects.update_forward_refs()
ReadAllAddressUuidsAddressesObjectsValidities.update_forward_refs()
ReadAllAddressUuidsAddressesObjectsValiditiesValidity.update_forward_refs()
ReadAllAddressUuidsAddressesPageInfo.update_forward_refs()
