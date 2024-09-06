from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class ReadAddressRelationUuids(BaseModel):
    addresses: "ReadAddressRelationUuidsAddresses"


class ReadAddressRelationUuidsAddresses(BaseModel):
    objects: list["ReadAddressRelationUuidsAddressesObjects"]


class ReadAddressRelationUuidsAddressesObjects(BaseModel):
    current: Optional["ReadAddressRelationUuidsAddressesObjectsCurrent"]


class ReadAddressRelationUuidsAddressesObjectsCurrent(BaseModel):
    employee_uuid: UUID | None
    org_unit_uuid: UUID | None


ReadAddressRelationUuids.update_forward_refs()
ReadAddressRelationUuidsAddresses.update_forward_refs()
ReadAddressRelationUuidsAddressesObjects.update_forward_refs()
ReadAddressRelationUuidsAddressesObjectsCurrent.update_forward_refs()
