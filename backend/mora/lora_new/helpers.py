from datetime import date
from datetime import datetime
from datetime import time

from mora import util
from mora.lora import ValidityLiteral


def validity_tuple(
    validity: ValidityLiteral, now: date | datetime | None = None
) -> tuple[date | datetime, date | datetime]:
    """Return (start, end) tuple of datetimes for Lora."""
    if now is None:
        now = util.parsedatetime(util.now())

    # NOTE: We must explicitly convert date to datetime since the minimum resolution of date is
    # one day, which means that the addition of timedelta(microseconds=1) later will silently
    # be ignored.
    if type(now) is date:
        now = datetime.combine(now, time.min)

    if validity == "past":
        return util.NEGATIVE_INFINITY, now

    if validity == "present":
        return now, now + util.MINIMAL_INTERVAL

    if validity == "future":
        return now, util.POSITIVE_INFINITY

    raise TypeError(
        f"Expected validity to be 'past', 'present' or 'future', but was {validity}"
    )
