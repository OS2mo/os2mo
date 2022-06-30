#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import re
import warnings
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID

from dateutil.parser import isoparse
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from pydantic.config import Extra
from pydantic.main import BaseModel

from .. import config
from .. import exceptions

# from ramodels.mo._shared import validate_cpr
# from ramodels.mo._shared import validate_names
# from ramodels.base import tz_isodate

try:
    import zoneinfo
except ImportError:  # pragma: no cover
    from backports import zoneinfo  # type: ignore


# --------------------------------------------------------------------------------------
# Employee model
# --------------------------------------------------------------------------------------

# Type aliases
DictStrAny = Dict[str, Any]


class ISOParseError(ValueError):
    """Error to raise when parsing of ISO-8601 datetime strings fails."""

    def __init__(self, fail_value: Any) -> None:
        """Initialise with a suiting description including the failing value."""
        super().__init__(
            f"Unable to parse '{fail_value}' as an ISO-8601 datetime string"
        )


def deprecation(message: str) -> None:
    """Raise a deprecation warning with `message` at stacklevel 2."""
    warnings.warn(message, DeprecationWarning, stacklevel=2)


def split_name(name: str) -> Tuple[str, str]:
    """Split a name into first and last name.

    Args:
        name: The name to split.

    Returns:
        A 2-tuple containing first and last name.
    """
    split = name.rsplit(" ", maxsplit=1)
    if len(split) == 1:
        split.append("")
    givenname, surname = split
    return givenname, surname


def validate_names(
    values: DictStrAny,
    name_key: str,
    givenname_key: str,
    surname_key: str,
    nick_name: bool,
) -> DictStrAny:
    """Validate a name value from a dictionary. Used in the Employee model validator.

    Args:
        values: Value dict to validate.
        name_key: The key for the name value.
        givenname_key: The key for the first name value.
        surname_key: The key for the last name value.

    Raises:
        ValueError: If both `name_key` and any of the `givenname_key`, `surname_key`
            are given, as they are mutually exclusive.

    Returns:
        The value dict, untouched.
    """
    if (
        (not nick_name)
        and (not values.get(name_key))
        and (not values.get(givenname_key))
        and (not values.get(surname_key))
    ):
        raise exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
            name="Missing name or givenname or surname"
        )

    if values.get(name_key) is not None:
        # Both name and given/surname are given erroneously
        if values.get(givenname_key) is not None or values.get(surname_key) is not None:
            raise ValueError(
                f"{name_key} and {givenname_key}/{surname_key} are mutually exclusive"
            )
        # If only name is given, raise a deprecation warning and generate given/surname
        else:
            deprecation(
                f"{name_key} will be deprecated in a future version. "
                f"Prefer {givenname_key}/{surname_key} where possible"
            )
            values[givenname_key], values[surname_key] = split_name(values[name_key])

    return values


# def validate_cpr(cpr_no: Optional[str]) -> Optional[str]:
def validate_cpr(cpr_no: str) -> Optional[str]:
    """Validate a Danish CPR number.
    Note that this function does not check whether a CPR number *exists*,
    just that it is valid according to the spec.

    Args:
        cpr_no (Optional[str]): CPR to check.

    Raises:
        ValueError: If the given CPR number does not conform to the spec.

    Returns:
        Optional[str]: The validated CPR number.
    """

    if not config.get_settings().cpr_validate_birthdate:
        return cpr_no

    if cpr_no is None:
        return None

    if not re.match(r"^\d{10}$", cpr_no):
        raise ValueError("CPR string is invalid.")

    # We only obtain the most significant digit of the code part, since it's
    # what we need for century calculations,
    # cf. https://da.wikipedia.org/wiki/CPR-nummer
    day, month = (cpr_no[0:2], cpr_no[2:4])
    year, code_msd = map(int, (cpr_no[4:6], cpr_no[6]))

    # TODO: let's do pattern matching in 3.10:
    # https://www.python.org/dev/peps/pep-0622/ <3
    century: int = 0
    if code_msd < 4:
        century = 1900
    elif code_msd in {4, 9}:
        if 0 <= year <= 36:
            century = 2000
        else:
            century = 1900
    elif 5 <= code_msd <= 8:
        if 0 <= year <= 57:
            century = 2000
        else:
            century = 1800

    try:
        date.fromisoformat(f"{century+year}-{month}-{day}")
    except Exception:
        raise ValueError("CPR number is invalid.")
    return cpr_no


def tz_isodate(dt: Any) -> datetime:
    DEFAULT_TZ = zoneinfo.ZoneInfo("Europe/Copenhagen")
    """Attempts to parse an incoming value as a timezone aware datetime.

    Args:
        dt (Any): Value to parse into timezone aware datetime.

    Raises:
        ISOParseError: If the incoming value cannot be parsed by dateutil's isoparser.

    Returns:
        Timezone aware datetime object.

        Note that the default {DEFAULT_TZ} is used.
    """
    # Using isoparse as fromisoformat does not handle all valid ISO-8601
    # Using datetime.fromisoformat as isoparse does not handle fractional timezones
    # It is a mess, but this way we get really close to covering our bases
    try:
        iso_dt = isoparse(str(dt))
    except ValueError:
        try:
            iso_dt = datetime.fromisoformat(str(dt))
        except ValueError:
            raise ISOParseError(dt)

    iso_dt = iso_dt if iso_dt.tzinfo else iso_dt.replace(tzinfo=DEFAULT_TZ)
    return iso_dt


class Org(BaseModel):
    name: Optional[str] = Field(description="Name of the organisation")
    user_key: Optional[str] = Field(
        description="Optional notes about org or department"
    )
    uuid: UUID = Field(description="Uuid of the org (Generated when org created)")


class MOEmployeeWrite(BaseModel):
    """
    Pydantic model for creation and updating of employees.
    """

    cpr_no: Optional[str] = Field(description="CPR number of the employee.")

    org: Org = Field(description="Org unit the employee belongs to")
    user_key: Optional[str] = Field(
        description="Optional notes to eg. employee org or department"
    )
    uuid: Optional[UUID] = Field(
        description="Uuid of the employee (Generated when employee created)"
    )
    name: Optional[str] = Field(
        description=(
            "The full name of the employee. "
            "This is deprecated, please use givenname/surname."
        )
    )
    givenname: Optional[str] = Field(description="Given name of the employee.")
    surname: Optional[str] = Field(description="Surname of the employee.")
    nickname: Optional[str] = Field(
        description=(
            "Full nickname of the employee. "
            "Deprecated, please use given name/surname parts if needed."
        )
    )

    nickname_givenname: Optional[str] = Field(
        description="Given name part of nickname of the employee, if applicable."
    )

    nickname_surname: Optional[str] = Field(
        description="Surname part of nickname of the employee, if applicable."
    )
    seniority: Optional[date] = Field(description="Seniority of the employee.")
    details: Optional[List] = Field(
        description=(
            "Details to be created for the employee. Note that when this is used, the"
            " employee reference is implicit in the payload."
        )
    )

    # Validating name vs givenname/surname as they are mutually exclusive
    @root_validator(pre=True)
    def validate_name(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(values, "name", "givenname", "surname", nick_name=False)

    # Validating nickname vs nick_givenname/nick_surname as they are mutually exclusive
    @root_validator(pre=True)
    def validate_nickname(cls, values: DictStrAny) -> DictStrAny:
        return validate_names(
            values, "nickname", "nickname_givenname", "nickname_surname", nick_name=True
        )

    # Validating cpr has correct syntax, in date-format.
    # Also checks if cpr should be validated as per flag
    # ("cpr_validate_birthdate") set in config.
    @validator("cpr_no", pre=True)
    def validate_cpr_no(cls, cpr: str) -> DictStrAny:
        return validate_cpr(cpr)

    # Attempts to parse an incoming value as a timezone aware datetime
    @validator("seniority", pre=True, always=True)
    def parse_seniority(cls, seniority: Optional[Any]) -> Optional[datetime]:
        return tz_isodate(seniority) if seniority is not None else None

    class Config:
        extra = Extra.forbid
