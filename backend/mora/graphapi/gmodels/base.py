# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
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


def to_parsable_timestamp(s: str) -> str:
    """Ensure ISO timestamp isn't too exotic.

    Prior to 1893-04-01, Denmark used an GMT offset of 50 minutes and 20 seconds[1,2].
    Even though ISO 8601-2:2019 allows for general durations for time offsets such as
    `<time>±[hh]:[mm]:[ss].[sss]` or `<time>±[n]H[n]M[n]S`, the former standards did
    not[3]. Therefore, many parsing libraries will fail to parse timestamps with such
    precision. This regex truncates these timestamps to ensure compatibility.

    TODO: Python's stdlib datetime dumping and parsing properly supports the latest
    standards. When we get rid of the LoRa and service APIs we should simply remove all
    the "clever" parsing libraries and only support actual ISO timestamps in GraphQL.
    Note that the Strawberry library itself also uses the broken dateutils library[4].

    [1] https://en.wikipedia.org/wiki/Time_in_the_Danish_Realm#History
    [2] `zdump -ivc 1900 Europe/Copenhagen`
    [3] https://en.wikipedia.org/wiki/ISO_8601#Other_time_offset_specifications
    [4] https://github.com/strawberry-graphql/strawberry/blob/main/strawberry/schema/types/base_scalars.py
    """
    return re.sub(r"\+00:5\d.*$", "+01:00", s)


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
        iso_dt = isoparse(to_parsable_timestamp(str(dt)))
    except ValueError:
        try:
            iso_dt = datetime.fromisoformat(str(dt))
        except ValueError:
            raise ISOParseError(dt)

    iso_dt = iso_dt if iso_dt.tzinfo else iso_dt.replace(tzinfo=DEFAULT_TZ)
    return iso_dt
