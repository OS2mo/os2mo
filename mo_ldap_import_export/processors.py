# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re

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
