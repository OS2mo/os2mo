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

from pydantic import BaseModel
from pydantic import Extra

from ramodels.exceptions import ISOParseError

try:
    import zoneinfo
except ImportError:  # pragma: no cover
    from backports import zoneinfo  # type: ignore


# --------------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------------

# TODO: Perhaps it's worth reading from e.g. env vars here
DEFAULT_TZ = zoneinfo.ZoneInfo("Europe/Copenhagen")

POS_INF = "infinity"
NEG_INF = "-infinity"

# --------------------------------------------------------------------------------------
# Base models
# --------------------------------------------------------------------------------------


class RABase(BaseModel):
    """Base model for RA data models."""

    # TODO: This is duplicated to each class that cannot be instantiated.
    # We should probably find a better solution.
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls is RABase:
            raise TypeError("RABase may not be instantiated")
        return super().__new__(cls)

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid


# --------------------------------------------------------------------------------------
# Base utils
# --------------------------------------------------------------------------------------
def tz_isodate(dt: Any) -> datetime:
    """Attempts to parse an incoming value as a timezone aware datetime.

    Args:
        dt (Any): Value to parse into timezone aware datetime.

    Raises:
        ISOParseError: If the incoming value cannot be parsed by dateutil's isoparser.

    Returns:
        Timezone aware datetime object.

        Note that the default {DEFAULT_TZ} is used.
    """
    try:
        iso_dt = datetime.fromisoformat(str(dt))
    except ValueError:
        raise ISOParseError(dt)

    iso_dt = iso_dt if iso_dt.tzinfo else iso_dt.replace(tzinfo=DEFAULT_TZ)
    return iso_dt
