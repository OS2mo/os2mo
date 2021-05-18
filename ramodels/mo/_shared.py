#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from typing import Optional
from uuid import UUID
from uuid import uuid4

from pydantic import Field
from pydantic import validator

from ramodels.base import RABase

# --------------------------------------------------------------------------------------
# MOBase
# --------------------------------------------------------------------------------------


class MOBase(RABase):
    def __new__(cls, *args, **kwargs) -> Any:
        if cls is MOBase:
            raise TypeError("MOBase may not be instantiated")
        return super().__new__(cls)

    uuid: UUID = Field(None)

    # Autogenerate UUID if necessary
    @validator("uuid", pre=True, always=True)
    def set_uuid(cls, _uuid: Optional[UUID]) -> UUID:
        return _uuid or uuid4()


# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class AddressType(RABase):
    uuid: UUID


class EngagementAssociationType(RABase):
    uuid: UUID


class EngagementRef(RABase):
    uuid: UUID


class EngagementType(RABase):
    uuid: UUID


class AssociationType(RABase):
    uuid: UUID


class JobFunction(RABase):
    uuid: UUID


class ManagerLevel(RABase):
    uuid: UUID


class ManagerType(RABase):
    uuid: UUID


class OrganisationRef(RABase):
    uuid: UUID


class OrgUnitHierarchy(RABase):
    uuid: UUID


class OrgUnitLevel(RABase):
    uuid: UUID


class OrgUnitRef(RABase):
    uuid: UUID


class OrgUnitType(RABase):
    uuid: UUID


class ParentRef(RABase):
    uuid: UUID


class PersonRef(RABase):
    uuid: UUID


class Primary(RABase):
    uuid: UUID


class Responsibility(RABase):
    uuid: UUID


class Validity(RABase):
    from_date: str = Field("1930-01-01", alias="from")
    to_date: Optional[str] = Field(None, alias="to")


class Visibility(RABase):
    uuid: UUID
