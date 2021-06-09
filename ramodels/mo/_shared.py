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
from typing import Dict
from typing import Optional
from uuid import UUID
from uuid import uuid4

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ramodels.base import RABase
from ramodels.base import tz_isodate

try:
    import zoneinfo
except ImportError:  # pragma: no cover
    from backports import zoneinfo  # type: ignore

UTC = zoneinfo.ZoneInfo("UTC")

# --------------------------------------------------------------------------------------
# MOBase
# --------------------------------------------------------------------------------------


class MOBase(RABase):
    """Base model for MO data models.

    Attributes:
        uuid: If not specified then it is auto generated
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
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


class MORef(RABase):
    """
    Attributes:
        uuid:
    """

    uuid: UUID


class AddressType(MORef):
    pass


class EngagementAssociationType(MORef):
    pass


class EngagementRef(MORef):
    pass


class EngagementType(MORef):
    pass


class AssociationType(MORef):
    pass


class JobFunction(MORef):
    pass


class ManagerLevel(MORef):
    pass


class ManagerType(MORef):
    pass


class OrganisationRef(MORef):
    pass


class OrgUnitHierarchy(MORef):
    pass


class OrgUnitLevel(MORef):
    pass


class OrgUnitRef(MORef):
    pass


class OrgUnitType(MORef):
    pass


class ParentRef(MORef):
    pass


class PersonRef(MORef):
    pass


class Primary(MORef):
    pass


class Responsibility(MORef):
    pass


class Validity(RABase):
    from_date: datetime = Field(alias="from")
    to_date: Optional[datetime] = Field(alias="to")

    @validator("from_date", pre=True, always=True)
    def parse_from_date(cls, from_date: Any) -> datetime:
        return tz_isodate(from_date)

    @validator("to_date", pre=True, always=True)
    def parse_to_date(cls, to_date: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(to_date) if to_date is not None else None

    @root_validator
    def check_from_leq_to(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # Note: the values of from_date & to_date are not changed here
        # just leq compared.
        cmp_from_dt, _to_dt = values.get("from_date"), values.get("to_date")
        cmp_to_dt = _to_dt if _to_dt else datetime.max.replace(tzinfo=UTC)
        if all([cmp_from_dt, cmp_to_dt]) and not (cmp_from_dt <= cmp_to_dt):
            raise ValueError("from_date must be less than or equal to to_date")
        return values


class Visibility(MORef):
    pass
