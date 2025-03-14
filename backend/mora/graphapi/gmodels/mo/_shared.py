# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import zoneinfo
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from mora.graphapi.gmodels.base import RABase
from mora.graphapi.gmodels.base import tz_isodate

UTC = zoneinfo.ZoneInfo("UTC")

# Type aliases
DictStrAny = dict[str, Any]


class UUIDBase(RABase):
    """Base model with autogenerated UUID."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls is UUIDBase:  # pragma: no cover
            raise TypeError("UUIDBase may not be instantiated")
        return super().__new__(cls)

    uuid: UUID = Field(
        None, description="UUID to be created. Will be autogenerated if not specified."
    )  # type: ignore

    # Autogenerate UUID if necessary
    @validator("uuid", pre=True, always=True)
    def set_uuid(cls, _uuid: UUID | None) -> UUID:
        return _uuid or uuid4()


class MOBase(UUIDBase):
    """Base model for MO data models."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls is MOBase:  # pragma: no cover
            raise TypeError("MOBase may not be instantiated")
        return super().__new__(cls)

    user_key: str = Field(
        None, description="Short, unique key. Defaults to object UUID."
    )  # type: ignore

    @validator("user_key", pre=True, always=True)
    def set_user_key(cls, user_key: Any | None, values: DictStrAny) -> str:
        if user_key or isinstance(user_key, str):
            return user_key
        return str(values["uuid"])

    @root_validator
    def validate_type(cls, values: DictStrAny) -> DictStrAny:
        if "type_" in cls.__fields__ and "type_" in values:
            field = cls.__fields__["type_"]

            if (
                not field.required and values["type_"] != field.default
            ):  # pragma: no cover
                raise ValueError(f"type may only be its default: '{field.default}'")
        return values


class MORef(RABase):
    """Reference base.

    Yes, this is a weird layer of indirection. It is simply modelled
    after how MO's API for writing is and not out of necessity.
    """

    uuid: UUID = Field(description="The UUID of the reference.")


class ITUserRef(MORef):
    """IT User reference."""


class OrgUnitRef(MORef):
    """Organisation unit reference."""


class OpenValidity(RABase):
    """Validity of a MO object with optional `from_date`."""

    from_date: datetime | None = Field(
        None, alias="from", description="Start date of the validity."
    )
    to_date: datetime | None = Field(
        None, alias="to", description="End date of the validity, if applicable."
    )

    @validator("from_date", pre=True, always=True)
    def parse_from_date(cls, from_date: Any | None) -> datetime | None:
        return tz_isodate(from_date) if from_date is not None else None

    @validator("to_date", pre=True, always=True)
    def parse_to_date(cls, to_date: Any | None) -> datetime | None:
        return tz_isodate(to_date) if to_date is not None else None

    @root_validator
    def check_from_leq_to(cls, values: dict[str, Any]) -> dict[str, Any]:
        # Note: the values of from_date & to_date are not changed here
        # just leq compared.
        _from_dt, _to_dt = values.get("from_date"), values.get("to_date")
        cmp_from_dt = _from_dt or datetime.min.replace(tzinfo=UTC)
        cmp_to_dt = _to_dt or datetime.max.replace(tzinfo=UTC)
        if all([cmp_from_dt, cmp_to_dt]) and not (cmp_from_dt <= cmp_to_dt):
            raise ValueError(
                f"from_date {cmp_from_dt} must be less than "
                f"or equal to to_date {cmp_to_dt}"
            )
        return values


class Validity(OpenValidity):
    """Validity of a MO object with required `from_date`."""

    from_date: datetime = Field(alias="from", description="Start date of the validity.")
