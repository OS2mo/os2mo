from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadAddressRelationUuids(BaseModel):
    addresses: "ReadAddressRelationUuidsAddresses"


class ReadAddressRelationUuidsAddresses(BaseModel):
    objects: List["ReadAddressRelationUuidsAddressesObjects"]


class ReadAddressRelationUuidsAddressesObjects(BaseModel):
    current: Optional["ReadAddressRelationUuidsAddressesObjectsCurrent"]


class ReadAddressRelationUuidsAddressesObjectsCurrent(BaseModel):
    employee_uuid: Optional[UUID]
    org_unit_uuid: Optional[UUID]


ReadAddressRelationUuids.update_forward_refs()
ReadAddressRelationUuidsAddresses.update_forward_refs()
ReadAddressRelationUuidsAddressesObjects.update_forward_refs()
ReadAddressRelationUuidsAddressesObjectsCurrent.update_forward_refs()
