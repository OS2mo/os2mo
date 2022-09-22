# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Any

from dateutil.parser import isoparse
from pydantic import BaseModel
from pydantic import Extra
from pydantic import root_validator

from ramodels.exceptions import ISOParseError

try:
    import zoneinfo
except ImportError:  # pragma: no cover
    from backports import zoneinfo  # type: ignore


# TODO: Perhaps it's worth reading from e.g. env vars here
DEFAULT_TZ = zoneinfo.ZoneInfo("Europe/Copenhagen")

POS_INF = "infinity"
NEG_INF = "-infinity"


class RABase(BaseModel):
    """Base model for RA data models."""

    # TODO: This is duplicated to each class that cannot be instantiated.
    # We should probably find a better solution.
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create a new model with the given base model as its base.

        Raises:
            TypeError: If the base model is instantiated directly.
        """
        if cls is RABase:
            raise TypeError("RABase may not be instantiated")
        return super().__new__(cls)

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid

    @root_validator(pre=True)
    def remove_integration_data(cls, values: dict[str, Any]) -> dict[str, Any]:
        values.pop("integration_data", None)
        values.pop("integrationsdata", None)
        return values


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
