#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime
from typing import Any
from typing import Optional
from uuid import UUID
from uuid import uuid4

from dateutil.tz import UTC
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ramodels.base import RABase
from ramodels.base import tz_isodate

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
    from_date: datetime = Field(tz_isodate("1930-01-01"), alias="from")
    to_date: Optional[datetime] = Field(alias="to")

    @validator("from_date", pre=True, always=True)
    def parse_from_date(cls, from_date: Any) -> datetime:
        return tz_isodate(from_date)

    @validator("to_date", pre=True, always=True)
    def parse_to_date(cls, to_date: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(to_date) if to_date is not None else None

    @root_validator
    def check_from_leq_to(cls, values):
        # Note: the values of from_date & to_date are not changed here
        # just leq compared.
        cmp_from_dt, _to_dt = values.get("from_date"), values.get("to_date")
        cmp_to_dt = _to_dt if _to_dt else datetime.max.replace(tzinfo=UTC)
        if all([cmp_from_dt, cmp_to_dt]) and not (cmp_from_dt <= cmp_to_dt):
            raise ValueError("from_date must be less than or equal to to_date")
        return values


class Visibility(RABase):
    uuid: UUID
