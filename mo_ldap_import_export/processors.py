# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import re

import structlog
from ramodels.mo._shared import validate_cpr


def _hide_cpr(cpr_string):
    """
    Takes a string and hides the last 4 digits of a cpr no.
    If there is one in the string
    """
    matches = re.finditer(r"\d{10}|\d{6}-\d{4}", cpr_string)

    for match in matches:
        end = match.end()
        cpr = match.group(0).replace("-", "")

        try:
            validate_cpr(cpr)
        except ValueError:
            continue
        else:
            # Mask the last 4 digits of a cpr number
            cpr_string = cpr_string[: end - 4] + "xxxx" + cpr_string[end:]

    return cpr_string


def mask_cpr(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """
    Looks for cpr numbers and masks them
    """
    for key, value in event_dict.items():
        # Avoid treating UNIX timestamps as CPR numbers
        if key == "timestamp":
            continue
        if isinstance(value, str):
            event_dict[key] = _hide_cpr(value)
        else:
            event_dict[key] = _hide_cpr(repr(value))
    return event_dict
